import datetime
import streamlit as st
import streamlit.components.v1 as components
from pyecharts.charts import *
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from cityid import city_X,main
import re
import base64


st.set_page_config(
page_title="天气预报",
page_icon=":rainbow:",
layout='wide')

@st.cache_data
def get_img_as_base64(file):
    with open(file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.title('🌤︎天气预报')
st.markdown('<br>',unsafe_allow_html=True)
st.markdown('<br>',unsafe_allow_html=True)

if 'first_visit' not in st.session_state:
    st.session_state.first_visit=True
else:
    st.session_state.first_visit=False
# 初始化全局配置
if st.session_state.first_visit:
    # 在这里可以定义任意多个全局变量，方便程序进行调用
    st.session_state.date_time=datetime.datetime.now() + datetime.timedelta(hours=8) # Streamlit Cloud的时区是UTC，加8小时即北京时间
    st.session_state.city_X=city_X
    st.balloons()
    st.snow()

S=st.sidebar.selectbox('请选择你的城市',st.session_state.city_X.keys())
Shi=st.sidebar.selectbox('请选择你的城市',st.session_state.city_X[S].keys())
xian=st.sidebar.selectbox('请选择你的城市',st.session_state.city_X[S][Shi].keys())


with st.container():
    forecast7Days,data_all = main(S,Shi,xian)
    yu=0
    if '转' in forecast7Days["天气"][0]:
        index_of_turn = forecast7Days["天气"][0].index('转')
        text_before_turn = forecast7Days["天气"][0][:index_of_turn]
        if len(re.findall('[雨加雪]',text_before_turn)) != 0:
            if re.findall('[雨加雪]',text_before_turn)[0] == '雨加雪':
                weather = 'winter'
                yu=1
        if len(re.findall('[冰雹]',text_before_turn)) != 0:
            if re.findall('[冰雹]',text_before_turn)[0] == '冰雹':
                weather = 'ice'
        if len(re.findall('[雨]',text_before_turn)) != 0:
            if re.findall('[雨]',text_before_turn)[0] == '雨' and yu==0:
                weather = 'rain'
        if len(re.findall('[雾]',text_before_turn)) != 0:
            if re.findall('[雾]',text_before_turn)[0] == '雾':
                weather = 'smog'
        if len(re.findall('[霾]',text_before_turn)) != 0:
            if re.findall('[霾]',text_before_turn)[0] == '霾':
                weather = 'smog'
        if len(re.findall('[晴]',text_before_turn)) != 0:
            if re.findall('[晴]',text_before_turn)[0] == '晴':
                weather = 'sunny'
        if len(re.findall('[雪]',text_before_turn)) != 0:
            if re.findall('[雪]',text_before_turn)[0] == '雪':
                weather = 'winter'
        if len(re.findall('[沙]',text_before_turn)) != 0:
            if re.findall('[沙]',text_before_turn)[0] == '沙':
                weather = 'dust'
        if len(re.findall('[尘]',text_before_turn)) != 0:
            if re.findall('[尘]',text_before_turn)[0] == '尘':
                weather = 'dust'
        if len(re.findall('[阴]',text_before_turn)) != 0:
            if re.findall('[阴]',text_before_turn)[0] == '阴':
                weather = 'cloudy'
        if len(re.findall('[云]',text_before_turn)) != 0:
            if re.findall('[云]',text_before_turn)[0] == '云':
                weather = 'cloudy'
    else:
        if len(re.findall('[雨加雪]',forecast7Days["天气"][0])) != 0:
            if re.findall('[雨加雪]',forecast7Days["天气"][0])[0] == '雨加雪':
                weather = 'winter'
                yu=1
        if len(re.findall('[冰雹]',forecast7Days["天气"][0])) != 0:
            if re.findall('[冰雹]',forecast7Days["天气"][0])[0] == '冰雹':
                weather = 'ice'
        if len(re.findall('[雨]',forecast7Days["天气"][0])) != 0:
            if re.findall('[雨]',forecast7Days["天气"][0])[0] == '雨' and yu==0:
                weather = 'rain'
        if len(re.findall('[雾]',forecast7Days["天气"][0])) != 0:
            if re.findall('[雾]',forecast7Days["天气"][0])[0] == '雾':
                weather = 'smog'
        if len(re.findall('[霾]',forecast7Days["天气"][0])) != 0:
            if re.findall('[霾]',forecast7Days["天气"][0])[0] == '霾':
                weather = 'smog'
        if len(re.findall('[晴]',forecast7Days["天气"][0])) != 0:
            if re.findall('[晴]',forecast7Days["天气"][0])[0] == '晴':
                weather = 'sunny'
        if len(re.findall('[雪]',forecast7Days["天气"][0])) != 0:
            if re.findall('[雪]',forecast7Days["天气"][0])[0] == '雪':
                weather = 'winter'
        if len(re.findall('[沙]',forecast7Days["天气"][0])) != 0:
            if re.findall('[沙]',forecast7Days["天气"][0])[0] == '沙':
                weather = 'dust'
        if len(re.findall('[尘]',forecast7Days["天气"][0])) != 0:
            if re.findall('[尘]',forecast7Days["天气"][0])[0] == '尘':
                weather = 'dust'
        if len(re.findall('[阴]',forecast7Days["天气"][0])) != 0:
            if re.findall('[阴]',forecast7Days["天气"][0])[0] == '阴':
                weather = 'cloudy'
        if len(re.findall('[云]',forecast7Days["天气"][0])) != 0:
            if re.findall('[云]',forecast7Days["天气"][0])[0] == '云':
                weather = 'cloudy'

    Home = get_img_as_base64(f'images/{weather}.jpg')
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
    st.markdown(f'### {xian} Weather') 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('天气',forecast7Days['天气'][0])
    col2.metric('气温',forecast7Days['气温'][0])
    col3.metric('风向',forecast7Days['风向'][0])
    col4.metric('风级',forecast7Days['风级'][0])
    

    current_month = datetime.datetime.now().month
    if 11>current_month>3:
        insect = {4:"金龟子",5:"食心虫",6:"蚜虫",7:"红蜘蛛",8:"卷叶蛾",9:"潜叶蛾",10:"介壳虫"}
        insect_kill = {4:"甲维高氯或阿维高氯",5:"甲维高氯、螺虫乙酯或阿维高氯",6:"吡虫啉、噻虫嗪",7:"阿维螺螨酯或联井乙螨唑",8:"呋虫胺",9:"呋虫胺",10:"石硫合剂或毒死蜱"}

        sicks = {4:"锈病",5:"黑星病",6:"炭疽叶枯病",7:"褐斑病",8:"斑点落叶病",9:"斑点落叶病",10:"圆斑病"}
        sicks_protect = {4:"吡唑醚菌脂",5:"甲基硫菌灵、苯醚甲环唑",6:"吡唑醚菌子",7:"丙森锌（安泰生）可湿性粉剂",8:"波尔多液",9:"波尔多液",10:"代森锰锌"}
        sick_kill = {4:"三唑酮或苯醚甲环唑",5:"杜邦福星乳油",6:"咪鲜胺或戊唑醇",7:"戊唑醇或丙环唑",8:"戊唑醇或丙环唑",9:"戊唑醇或丙环唑",10:"甲基硫菌灵或咪鲜胺"}

        col1, col2 = st.columns(2)
        col1.markdown(f'''
                #### 当前月份为 _:red[{insect[current_month]}]_ 虫害高发期
                #### 杀虫剂 _:red[{insect_kill[current_month]}]_
                ''')
        col2.markdown(f'''
                #### 当前月份为 _:red[{sicks[current_month]}]_ 病害高发期
                #### 预防药物 _:red[{sicks_protect[current_month]}]_
                #### 治疗药物 _:red[{sick_kill[current_month]}]_
                ''')
    
    
    c1 = (
        Line()
        .add_xaxis(xaxis_data=forecast7Days.index.to_list())
        .add_yaxis(series_name="最高气温",y_axis=forecast7Days["最高气温"].str.replace("℃", ""))
        .add_yaxis(series_name="最低气温",y_axis=forecast7Days["最低气温"].str.replace("℃", ""))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="7日气温变化"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
            )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True,formatter=JsCode("function(x){return x.data[1] + '°C';}")))
    )

    c2 = (
        Line()
        .add_xaxis(xaxis_data=data_all.index.to_list())
        .add_yaxis(series_name="最高气温",y_axis=data_all["最高气温"].str.replace("℃", ""))
        .add_yaxis(series_name="最低气温",y_axis=data_all["最低气温"].str.replace("℃", ""))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="15日气温变化"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
            )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True,formatter=JsCode("function(x){return x.data[1] + '°C';}")))
    )

    t = Timeline(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width='1200px'))
    t.add_schema(play_interval=10000,is_auto_play=True)
    t.add(c1, "7天 Forecast")
    t.add(c2, "15天 Forecast")
    components.html(t.render_embed(), width=1200, height=520)



    # 霜冻
    current_day = datetime.datetime.now().day

    if current_month==4 and current_day>8:
        count = 0
        for i in range(1,15):
            if int(re.findall('[0-9]{1,2}',data_all["最高气温"][i])[0]) < -2:
                count += 1

        if count > 0:
            st.markdown('''
                ## :red[**近期霜冻概率较高**]
            * 预防措施
                * 熏烟法：（地理中称为“人造烟雾”）在霜冻之夜，用烟雾较大、
                    略潮湿一点的柴草麦秸、残枝落叶、锯末等为原料，或用防霜烟雾剂进行烟熏。
                    在田间熏烟可有效地减轻避免霜冻灾害。这些烟雾能够增强大气逆辐射，
                    对地面起保温作用，阻挡地面热量的散失，而烟雾本身也会产生一定的热量。\n
                * 喷水法：在霜冻发生前，用喷雾器对植株表面喷水，可使其体温下降缓慢，
                    而且可以增加大气中水蒸气含量，水气凝结放热，以缓和霜害。明显的霜冻天，
                    可多次喷水。喷水可以增加空气湿度，增强大气逆辐射，对地面起保温作用，减小温差。\n
                * 霜前灌水法：低温来临前3-5天灌水,防效最好。霜前灌水，晚上水温比土温高，
                    水可使土壤增加大量的热量。灌水的作用一是可以增加土壤的热容量，使土壤降温慢，
                    土壤温度不会下降很快，二是可增加近地面层空气湿度。增加大气逆辐射，对地面起保温作用，
                    保护地面热量。
                        ''')
    # 冰雹
    if forecast7Days['天气'].isin(['冰雹']).any():
        st.markdown('''
            ## :red[**当心冰雹！！！注意提前铺设防雹网**]
            ''')


    # 降雨
    if 11>current_month>3:
        cnt=0
        for i in range(1,7):
            if len(re.findall('[雨]',forecast7Days["天气"][i])) != 0:
                if re.findall('[雨]',forecast7Days["天气"][i])[0] == '雨' :
                    cnt += 1
        if cnt >= 3:
            st.markdown('''
            ## :red[**持续降雨预警！！！参照当月高发病害，做出对应管理措施**]
            ''')

    # 干旱高温
    if 11>current_month>3:
        cnt=0
        for i in range(1,15):
            if len(re.findall('[晴]',data_all["天气"][i])) != 0:
                if re.findall('[晴]',data_all["天气"][i])[0] == '晴' and int(re.findall('[0-9]{1,2}',data_all["最低气温"][i])[0]) > 30:
                    cnt += 1
        if cnt >= 12 :
            st.markdown('''
            ## :red[**高温干旱预警！！！参照当月高发虫害，做出对应管理措施**]
            ''')


    with st.expander("7日天气预报",expanded=True):
        st.table(forecast7Days)
    with st.expander("15日天气预报",expanded=True):
        st.table(data_all)



