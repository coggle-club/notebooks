import streamlit as st
import os

import time
import jwt
import requests

def ask_gpt(key, model, max_tokens, temperature, content):
    url = "https://openai.api2d.net/v1/chat/completions"
    # 可以从 https://api2d.com 购买api，然后国内直接链接

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + key
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
    st.title('通过API与大模型的对话')
    # st.write('支持的大模型包括的ChatGLM3和4')
    if 'API_TOKEN' in st.session_state and len(st.session_state['API_TOKEN']) > 1:
        st.success('API Token已经配置', icon='✅')
        key = st.session_state['API_TOKEN']
    else:
        key = ""

    key = st.text_input('输入Token:', type='password', value=key)

    st.session_state['API_TOKEN'] = key

    model = st.selectbox("选择模型", ["gpt-3.5-turbo-0613", "gpt-4-0613"])
    max_tokens = st.slider("max_tokens", 0, 2000, value=512)
    temperature = st.slider("temperature", 0.0, 2.0, value=0.8)

# 初始化的对话
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "你好我是ChatGPT，有什么可以帮助你的？"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "你好我是ChatGPT，有什么可以帮助你的？"}]

st.sidebar.button('清空聊天记录', on_click=clear_chat_history)


if len(key) > 1:
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("请求中..."):
                full_response = ask_gpt(key, model, max_tokens, temperature, st.session_state.messages)['choices'][0]['message']['content']
                st.markdown(full_response)

                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)