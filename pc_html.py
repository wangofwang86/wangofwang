

import streamlit as st
from openai import OpenAI
import PyPDF2  # 用于解析 PDF 的核心库

# --- 1. 初始化页面配置 ---
st.set_page_config(page_title="AI 创业实战助手", layout="wide")

#api_key = st.secrets["DEEPSEEK_KEY"]
# --- 3. 初始化 AI 客户端 ---
# 这里建议加上判断，防止没填 Key 就运行
client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"] ,base_url="https://api.deepseek.com")
# --- 2. 初始化 DeepSeek 客户端 ---
# 这里使用了 Streamlit 的 Secrets 功能来保护你的 API Key

# --- 3. 定义 PDF 处理逻辑 (底层逻辑：数据清洗) ---
def read_pdf(file):
    """从 PDF 文件中提取纯文本内容"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        # 逐页提取文字并拼接
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

# --- 4. 初始化聊天记录 (底层逻辑：状态管理) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. 侧边栏布局 (用户交互设计) ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    
    # 文件上传组件
    uploaded_file = st.file_uploader("📂 上传参考文档 (PDF/TXT)", type=['pdf', 'txt'])
    
    file_content = ""
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            file_content = read_pdf(uploaded_file)
        else:
            file_content = uploaded_file.read().decode("utf-8")
        st.success("✅ 文档加载成功！")
        
        # 预览功能：增强用户对数据的感知
        with st.expander("查看提取的内容预览"):
            st.text(file_content[:1000] + "...")

    # 清空按钮
    if st.button("🧹 清空对话历史"):
        st.session_state.messages = []
        st.rerun()

# --- 6. 聊天界面展示 ---
st.title("🤖 你的 AI 文档顾问")
st.caption("上传一份 PDF，我会基于文档内容回答你的问题。")

# 渲染历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. 对话核心逻辑 (底层逻辑：Prompt 工程) ---
if prompt := st.chat_input("请问我关于文档的任何问题..."):
    
    # 展示用户输入
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 构造发送给 AI 的消息列表
    # 创业技巧：使用 System Prompt 进行“任务锚定”
    messages_to_send = []
    
    # 如果有上传文件，则将文件内容作为“上下文”注入
    if file_content:
        messages_to_send.append({
            "role": "system", 
            "content": f"你是一个专业的文档分析专家。以下是用户上传的文档内容：\n\n{file_content}\n\n请严格基于上述内容回答。如果内容中没有相关信息，请诚实说明。"
        })
    else:
        messages_to_send.append({
            "role": "system", 
            "content": "你是一个有用的 AI 助手。"
        })

    # 合并历史对话记录
    messages_to_send.extend(st.session_state.messages)
    messages_to_send.append({"role": "user", "content": prompt})

    # 调用 API 并流式输出
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages_to_send,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)

    # 将本次对话存入记忆
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_response})
