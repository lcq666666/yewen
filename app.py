import streamlit as st
import base64

st.set_page_config(
    page_title="云春·叶问",
    page_icon="👨‍🌾",
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

Home = get_img_as_base64('images/Home.png')
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
opacity: 1;
}}
</style>
'''

st.markdown(page_bg_img,unsafe_allow_html=True)

st.write("# 欢迎来到云春·叶问! 👋")
st.sidebar.success("在上方切换板块")


st.markdown("## 板块一 苹果叶片病害识别")
st.markdown("**苹果叶片检测使用模型**：_mobilenet_v3_large_")
st.markdown("**苹果叶片检测训练数据**：分别为斑点落叶病、黑腐病、褐斑病、灰斑病、花叶病、锈病、黑星病七种病害共30927张图，_训练集_:28000 _测试集_:2927")
st.markdown("## 板块二 农业知识问答")
st.markdown("**农业知识问答使用模型**：_Qwen1.5-0.5B-Chat_")
st.markdown("**训练数据(数据库)**：果园管理100问:3782条")
st.markdown("## 板块三 天气预报")
st.markdown("**天气预测数据来源**：[中国天气网](http://www.weather.com.cn/)")
st.markdown("**👈 点击左侧栏**，快速使用吧！")
st.markdown("""
    ### 想了解更多吗？
    ### 相关学习资料
    - [开源大模型使用指南 GitHub](https://github.com/datawhalechina/self-llm)
    - [Qwen1.5-0.5B-Chat modelscope 模型下载](https://www.modelscope.cn/models/qwen/Qwen1.5-0.5B-Chat/summary)
    - [MobileNetV3 论文](https://arxiv.org/abs/1905.02244)
    """
)