import os
from pickle import NONE
import time
from xml.etree.ElementInclude import include
import jwt

import streamlit as st
import pandas as pd
import requests

import re
def extract_code_blocks(markdown_content):
    code_blocks = re.findall(r'```(.*?)```', markdown_content, re.DOTALL)
    return code_blocks

# 实际KEY，过期时间
def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )

def ask_glm(key, model, max_tokens, temperature, content):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
      'Content-Type': 'application/json',
      'Authorization': generate_token(key, 1000)
    }

    data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": content
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

st.set_page_config(page_title="聊天机器人")

with st.sidebar:
    st.title('通过大模型进行数据分析')
    if 'API_TOKEN' in st.session_state and len(st.session_state['API_TOKEN']) > 1:
        st.success('API Token已经配置', icon='✅')
        key = st.session_state['API_TOKEN']
    else:
        key = "7bf001734ef2fd7f7a55bf51dadd7cbb.BMAsoKRDFTmTEPwj"

    key = st.text_input('输入Token:', type='password', value=key)

    st.session_state['API_TOKEN'] = key

    model = st.selectbox("选择模型", ["glm-3-turbo", "glm-4"])
    max_tokens = st.slider("max_tokens", 0, 2000, value=512)
    temperature = st.slider("temperature", 0.0, 2.0, value=0.8)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "你好我是ChatGLM，我可以自动的帮你进行数据分析和建模。"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if "dataframe" not in st.session_state.keys():
    uploaded_file = st.file_uploader("上传你需要分析的文件")
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe.head(10))
        st.session_state["dataframe"] = dataframe
    else:
        dataframe = None
else:
    dataframe = st.session_state["dataframe"]

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "你好我是ChatGLM，有什么可以帮助你的？"}]

st.sidebar.button('清空聊天记录', on_click=clear_chat_history)

print(len(st.session_state.messages))

if len(key) > 1 and len(st.session_state.messages) == 1 and dataframe is not None:
    data_info = f'''在python代码总，表格变量命名为df，数据集维度为：{dataframe.shape}，列名为：{dataframe.columns}

字段类型为：
{dataframe.dtypes.to_markdown()}
'''
    with st.chat_message("user"):
        st.markdown(data_info)
    st.session_state.messages.append({"role": "user", "content": data_info})
if len(key) > 1 and dataframe is not None:
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("请求中..."):
                full_response = ask_glm(key, model, max_tokens, temperature, st.session_state.messages)['choices'][0]['message']['content']
                full_code = extract_code_blocks(full_response)
                full_code = [x.replace("python\n", "") for x in full_code if 'python' in x]
                for x in full_code:
                    st.code(x)
                st.session_state.messages = st.session_state.messages[:-1]