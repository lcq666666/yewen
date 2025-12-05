import streamlit as st
from PIL import Image 
from torchvision import transforms
import torchvision.models as models
import torch
from sick import class_sick
import base64

st.set_page_config(
    page_title="苹果叶片病害识别",
    page_icon="🍎",
)

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

Home = get_img_as_base64('images/leaf.png')
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
background-image:url("data:image/jpg;base64,{Home}");
background-size: cover;
}}
</style>
'''

st.markdown(page_bg_img,unsafe_allow_html=True)

model = models.mobilenet_v3_large()

model.load_state_dict(torch.load('best_MobileV3_L_model_end.pkl',map_location=torch.device('cpu')))


st.title('🍃苹果叶片病害识别')

DEMO_IMAGE = 'Test.jpg'

transformers = transforms.Compose([transforms.Resize(size=(232))
                                     ,transforms.RandomResizedCrop(224)  # 反转
                                     ,transforms.ToTensor()
                ])

def output(image):
    img = Image.open(image)
    img = transformers(img)
    img = torch.unsqueeze(img,dim=0)
    model.eval()
    pred = model(img)
    _, predict= torch.max(pred.data,dim=1)
    return predict.item()

def get_key(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None 
img_file_buffer = st.file_uploader("点击“Browse files”上传叶子图片", type=["png", "jpg", "jpeg"])
if img_file_buffer is not None:
    image = img_file_buffer
else:
    st.header('识别样例')
    demo_image = DEMO_IMAGE
    image = demo_image

result = output(image)
class_mapping = {"斑点落叶病":0,"褐斑病":1,"黑腐病":2,
                         "灰斑病":3,"花叶病":4,"锈病":5,"黑星病":6}

st.image(
    image, caption=f"叶子图片", use_column_width=True,
)

key = get_key(class_mapping,result)


st.markdown(f"""
        识别结果为: 
        ## {key}
    """)


st.markdown(class_sick[key])
