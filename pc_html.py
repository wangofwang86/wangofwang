import streamlit as st
from openai import OpenAI
import json
import os
temp=0.7
# --- 1. 页面设置 ---
st.set_page_config(page_title="DeepSeek 智聊", page_icon="🚀", layout="wide")

# --- 2. 侧边栏：参数调节与存档管理 ---
with st.sidebar:
    st.title("🤖 助手设置")
    st.info("在这里可以管理你的对话")
    st.title("⚙️ 配置")
    # 这里定义的 temp 只在侧边栏逻辑里生效
    temp = st.slider("创造力", 0.0, 2.0, 0.7)
    # 添加一个明显的按钮
    if st.button("🧹 清空当前对话", use_container_width=True):
        # 核心逻辑：重置 session_state 里的消息列表
        st.session_state.messages = [
            {"role": "system", "content": "你是一个友善的网页助手。"}
        ]
        # 强制刷新页面，让气泡消失
        st.rerun()

    st.divider() # 画一条分割线
    st.write("当前记忆长度：", len(st.session_state.get("messages", [])))
api_key = st.secrets["DEEPSEEK_KEY"]
# --- 3. 初始化 AI 客户端 ---
# 这里建议加上判断，防止没填 Key 就运行
client = OpenAI(api_key="DEEPSEEK_KEY" ,base_url="https://api.deepseek.com")

# --- 4. 记忆恢复（关联之前的 messages） ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "你是一个助手"}]

# --- 5. 渲染聊天气泡 ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. 聊天逻辑：引入【流式输出】 ---
if prompt := st.chat_input("说点什么吧..."):
    # 用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 回复（打字机效果）
    with st.chat_message("assistant"):
        # 创建一个空容器用来放文字
        response_placeholder = st.empty()
        full_response = ""
        
        # 开启 stream=True
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            temperature=temp,
            stream=True  # 开启流式传输
        )
        
        # 逐个字符蹦出来
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌") # 加个光标
        
        response_placeholder.markdown(full_response) # 完成后去掉光标
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})