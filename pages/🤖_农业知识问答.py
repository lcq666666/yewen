import copy
import warnings
from typing import Callable, List, Optional
import streamlit as st
import torch
from torch import nn
from transformers.generation.utils import (LogitsProcessorList,
                                           StoppingCriteriaList)
from transformers.utils import logging
# 核心修改1：引入官方 GenerationConfig，不再使用 dataclass 自定义
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import base64

logger = logging.get_logger(__name__)

st.set_page_config(
    page_title="农业知识问答",
    page_icon="🤖",
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 核心修改2：generate_interactive 函数逻辑调整，适配官方 GenerationConfig 对象
@torch.inference_mode()
def generate_interactive(
    model,
    tokenizer,
    prompt,
    generation_config: Optional[GenerationConfig] = None,
    logits_processor: Optional[LogitsProcessorList] = None,
    stopping_criteria: Optional[StoppingCriteriaList] = None,
    prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor],
                                                List[int]]] = None,
    additional_eos_token_id: Optional[int] = None,
    **kwargs,
):
    inputs = tokenizer([prompt], padding=True, return_tensors='pt')
    input_length = len(inputs['input_ids'][0])
    for k, v in inputs.items():
        # 如果你有GPU，请取消下面这行的注释
        # inputs[k] = v.cuda()
        inputs[k] = v
    input_ids = inputs['input_ids']
    _, input_ids_seq_length = input_ids.shape[0], input_ids.shape[-1]
    
    if generation_config is None:
        generation_config = model.generation_config
    
    # 使用官方对象的 copy 方法
    generation_config = copy.deepcopy(generation_config)
    
    # 更新配置
    model_kwargs = generation_config.update(**kwargs)
    
    bos_token_id, eos_token_id = (
        generation_config.bos_token_id,
        generation_config.eos_token_id,
    )
    if isinstance(eos_token_id, int):
        eos_token_id = [eos_token_id]
    if additional_eos_token_id is not None:
        eos_token_id.append(additional_eos_token_id)
        
    has_default_max_length = kwargs.get(
        'max_length') is None and generation_config.max_length is not None
        
    if has_default_max_length and generation_config.max_new_tokens is None:
        warnings.warn(
            f"Using 'max_length''s default ({repr(generation_config.max_length)}) to control the generation length. "
            "This behaviour is deprecated. recommend using `max_new_tokens`.",
            UserWarning,
        )
    elif generation_config.max_new_tokens is not None:
        generation_config.max_length = generation_config.max_new_tokens + input_ids_seq_length

    logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
    stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()

    logits_processor = model._get_logits_processor(
        generation_config=generation_config,
        input_ids_seq_length=input_ids_seq_length,
        encoder_input_ids=input_ids,
        prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
        logits_processor=logits_processor,
    )

    stopping_criteria = model._get_stopping_criteria(
        generation_config=generation_config,
        stopping_criteria=stopping_criteria)
    logits_warper = model._get_logits_warper(generation_config)

    unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
    scores = None
    while True:
        model_inputs = model.prepare_inputs_for_generation(
            input_ids, **model_kwargs)
        # forward pass to get next token
        outputs = model(
            **model_inputs,
            return_dict=True,
            output_attentions=False,
            output_hidden_states=False,
        )

        next_token_logits = outputs.logits[:, -1, :]

        # pre-process distribution
        next_token_scores = logits_processor(input_ids, next_token_logits)
        next_token_scores = logits_warper(input_ids, next_token_scores)

        # sample
        probs = nn.functional.softmax(next_token_scores, dim=-1)
        if generation_config.do_sample:
            next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
        else:
            next_tokens = torch.argmax(probs, dim=-1)

        # update generated ids, model inputs, and length for next step
        input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
        model_kwargs = model._update_model_kwargs_for_generation(
            outputs, model_kwargs, is_encoder_decoder=False)
        unfinished_sequences = unfinished_sequences.mul(
            (min(next_tokens != i for i in eos_token_id)).long())

        output_token_ids = input_ids[0].cpu().tolist()
        output_token_ids = output_token_ids[input_length:]
        for each_eos_token_id in eos_token_id:
            if output_token_ids[-1] == each_eos_token_id:
                output_token_ids = output_token_ids[:-1]
        response = tokenizer.decode(output_token_ids)

        yield response
        
        if unfinished_sequences.max() == 0 or stopping_criteria(
                input_ids, scores):
            break


def on_btn_click():
    del st.session_state.messages


@st.cache_resource(max_entries=10, ttl=3600)
def load_model():
    # 确保路径正确指向你的 merge_model 文件夹
    model = AutoModelForCausalLM.from_pretrained("merge_model",
                                                trust_remote_code=True, 
                                                torch_dtype=torch.float32, 
                                                device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained("qwen/Qwen1.5-0.5B-Chat", trust_remote_code=True)
    return model, tokenizer


def prepare_generation_config():
    with st.sidebar:
        top_p = st.slider('Top-p(累积概率)', 0.0, 1.0, 0.8, step=0.01)
        st.button('清除历史对话', on_click=on_btn_click)

    # 核心修改3：实例化官方 GenerationConfig，手动赋值参数
    generation_config = GenerationConfig()
    generation_config.max_length = 32768
    generation_config.top_p = top_p
    generation_config.do_sample = True
    generation_config.repetition_penalty = 1.005
    # Qwen 特有配置
    generation_config.pad_token_id = 151643
    generation_config.eos_token_id = [151645, 151643]

    return generation_config


user_prompt = '<|im_start|>user\n{user}<|im_end|>\n'
robot_prompt = '<|im_start|>assistant\n{robot}<|im_end|>\n'
cur_query_prompt = '<|im_start|>user\n{user}<|im_end|>\n\
    <|im_start|>assistant\n'


def combine_history(prompt):
    messages = st.session_state.messages
    meta_instruction = ('现在你要扮演一个专业的果树农业大师--果小艺，你要根据用户的农业问题做出中文回答.')
    total_prompt = f"<s><|im_start|>system\n{meta_instruction}<|im_end|>\n"
    for message in messages:
        cur_content = message['content']
        if message['role'] == 'user':
            cur_prompt = user_prompt.format(user=cur_content)
        elif message['role'] == 'robot':
            cur_prompt = robot_prompt.format(robot=cur_content)
        else:
            raise RuntimeError
        total_prompt += cur_prompt
    total_prompt = total_prompt + cur_query_prompt.format(user=prompt)
    return total_prompt


def main():
    Home = get_img_as_base64('images/bg.jpg')
    sidebar = get_img_as_base64('images/sidebar.jpg')

    page_bg_img=f'''
    <style>
    [data-testid="collapsedControl"] svg {{
        height: 3rem;
        width: 3rem;
    }}

    [data-testid="stSidebar"]{{
    background-image:url("data:image/jpg;base64,{sidebar}");
    background-size: cover;
    }}

    [data-testid="stHeader"]{{
    background-color: rgba(0,0,0,0);
    }}

    [data-testid="stAppViewContainer"]{{
    background-image:url("data:image/png;base64,{Home}");
    background-size: cover;
    }}

    [data-testid="stBottom"] > div {{
        background: transparent;
    }}
    </style>
    '''

    st.markdown(page_bg_img,unsafe_allow_html=True)
    print('load model begin.')
    model, tokenizer = load_model()
    print('load model end.')

    user_avator = '🧑‍🌾'
    robot_avator = '🤖'

    st.title('💭农业知识问答')

    generation_config = prepare_generation_config()

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message['role'], avatar=message.get('avatar')):
            st.markdown(message['content'])

    # Accept user input
    if prompt := st.chat_input('请在这里输入问题'):
        # Display user message in chat message container
        with st.chat_message('user', avatar=user_avator):
            st.markdown(prompt)
        real_prompt = combine_history(prompt)
        # Add user message to chat history
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt,
            'avatar': user_avator
        })

        with st.chat_message('robot', avatar=robot_avator):
            message_placeholder = st.empty()
            
            # 核心修改4：传递 generation_config 对象，移除 asdict 调用
            for cur_response in generate_interactive(
                    model=model,
                    tokenizer=tokenizer,
                    prompt=real_prompt,
                    generation_config=generation_config,
                    additional_eos_token_id=92542,
            ):
                message_placeholder.markdown(cur_response + '▌')
            message_placeholder.markdown(cur_response)
        
        st.session_state.messages.append({
            'role': 'robot',
            'content': cur_response, 
            'avatar': robot_avator,
        })

if __name__ == '__main__':
    main()
