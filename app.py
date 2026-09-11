"""前端：只负责界面 + 发请求"""
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# 加载 .env（前端本身不需要密钥，但保留以便显示状态）
load_dotenv()

# ========== 后端地址 ==========
API_BASE_URL = "http://localhost:8000"

# ========== 页面配置 画页面==========
st.set_page_config(page_title="智能聊天机器人", page_icon="🤖", layout="centered")

# ========== 注入 CSS 样式：固定输入框到底部 设置浏览器标签页的标题和图标==========
st.markdown("""
    <style>
        .main .block-container {
            padding-bottom: 120px;
        }
        .stChatInputContainer {
            position: fixed !important;
            bottom: 0px !important;
            left: 0px !important;
            right: 0px !important;
            background-color: #0e1117;
            padding: 10px 20px 15px 20px;
            z-index: 999;
            border-top: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
"""在页面左边画一个侧边栏
画一个单选按钮，默认选中 "本地 Ollama"（index=0）
用户的选择会存到变量 backend_type 里"""
with st.sidebar:

    st.title("⚙️ 模型设置")

    backend_type = st.radio(
        "选择模型来源",
        ["本地 Ollama", "云端 DeepSeek"],
        index=0
    )


    """
    如果用户选"本地"，显示本地模型下拉菜单（llama3.2:3b 等）
    如果用户选"云端"，显示 DeepSeek 模型下拉菜单
    如果 .env 里没配置密钥，显示警告
    """
    if backend_type == "本地 Ollama":
        model_name = st.selectbox("本地模型", ["llama3.2:3b", "qwen2.5:7b", "mistral", "gemma2:9b"])
        #提示
        st.caption("确保 Ollama 服务已启动（ollama serve）")
    else:
        model_name = st.selectbox("DeepSeek 模型", ["deepseek-chat", "deepseek-v4-flash-vision-exp"])
        st.caption("使用 DeepSeek API，需在 .env 中配置 DEEPSEEK_API_KEY")
        if not os.getenv("DEEPSEEK_API_KEY"):
            st.warning("⚠️ 未检测到 DEEPSEEK_API_KEY，请在 .env 文件中配置")

    """画一条分割线
    画一个下拉菜单，让用户选择提示词策略（默认 zero_shot）
    这个策略会传给后端，决定模型怎么回答"""
    st.divider()
    # ========== 多选策略 ==========
    st.subheader("🧠 提示词策略（可多选）")

    strategies = st.multiselect(
        "选择策略组合",
        options=["zero_shot", "few_shot", "cot", "structured"],
        default=["zero_shot"],  # 默认至少选一个
        help="可同时选择多个策略，实现叠加效果"
    )

    # 如果用户一个都没选，默认给 zero_shot
    if not strategies:
        strategies = ["zero_shot"]
        st.info("已自动选择 zero_shot 作为默认策略")

    # 如果选了 few_shot，显示场景选择
    few_shot_category = None
    if "few_shot" in strategies:
        few_shot_category = st.selectbox(
            "Few-shot 场景",
            ["sentiment", "qa"],
            help="sentiment=情感分析；qa=问答"
        )

    # 如果选了 cot，显示任务描述
    task_description = None
    if "cot" in strategies:
        task_description = st.text_input(
            "任务描述（CoT 场景用）",
            placeholder="例如：请帮助用户解决编程问题"
        )
    # 画一个按钮，点击后清空聊天记录，并刷新页面
    if st.button("🗑️ 清空对话历史"):
        st.session_state.messages = []
        st.rerun()

# ========== 初始化 session_state ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== 主界面 ==========
tab1, tab2 = st.tabs(["💬 对话", "🖼️ 图像理解"])

# ---------- 标签1：对话 ----------
with tab1:
    st.title("🤖 智能聊天机器人")
    st.caption("支持本地 Ollama 或云端 DeepSeek，多轮对话上下文，支持多种提示词策略")

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    #st.chat_input 是一个输入框，用户输入后按回车，它会返回输入的内容
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        #将用户消息画个泡泡显示
        with st.chat_message("user"):
            st.markdown(prompt)
        #先画一个空的"助手气泡"，准备放 AI 的回答
        with st.chat_message("assistant"):
            # 创建一个"占位符"，后续可以用它来动态更新内容
            placeholder = st.empty()
            #准备一个空字符串，用来拼接 AI 的回答
            full_response = ""

            try:
                # 构建请求体（历史消息）
                #把 session_state.messages 转换成后端需要的格式（列表里每个元素都是 {"role": "user", "content": "你好"} 这样的字典）。
                messages_for_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                # 准备请求参数
                payload = {
                    "messages": messages_for_api, #历史消息
                    "model": model_name, #用户选的模型
                    "backend": "ollama" if backend_type == "本地 Ollama" else "deepseek", #用户选的后端（本地/云端）
                    "stream": True,#是否流式输出
                    "strategies": strategies,  # 放这里
                    "few_shot": few_shot_category or "",
                    "task": task_description or ""
                }

                params = {
                    "strategies": strategies,#提示词策略，这里是复数，传列表
                    "few_shot": few_shot_category or "",#Few-shot 场景（如果有）
                    "task": task_description or ""#CoT 任务描述（如果有）
                }

                #前端通过 HTTP 协议，向后端 http://localhost:8000/chat/stream 发送 POST 请求
                # 请求体是 JSON 格式（payload）
                # URL 参数是 strategies、few_shot、task
                # stream=True 表示启用流式模式（后端边生成边返回）
                # timeout=60 表示最多等待 60 秒
                # 发送流式请求到 FastAPI
                response = requests.post(
                    f"{API_BASE_URL}/chat/stream",
                    json=payload,
                    stream=True,
                    timeout=60
                )

                # 检查状态码
                if response.status_code != 200:
                    st.error(f"后端返回错误: {response.status_code} - {response.text}")
                    st.stop()

                # 逐块读取流式响应
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确认 FastAPI 已启动（uvicorn backend.main:app --reload）")
            except Exception as e:
                st.error(f"调用出错: {e}")

# ---------- 标签2：图像理解 ----------
with tab2:
    st.title("🖼️ DeepSeek 图像理解")
    st.caption("使用 DeepSeek Vision 模型分析图片内容（仅云端）")

    if not os.getenv("DEEPSEEK_API_KEY"):
        st.error("❌ 请先配置 DEEPSEEK_API_KEY 才能使用图像理解功能")
        st.stop()

    input_type = st.radio("选择图片来源", ["图片 URL", "上传本地图片"])

    image_url = None
    uploaded_file = None

    if input_type == "图片 URL":
        image_url = st.text_input(
            "输入图片 URL",
            "https://pic.rmb.bdstatic.com/8859ebddde6c7d462218176a81135c9a.jpg@h_1280"
        )
    else:
        uploaded_file = st.file_uploader("上传图片", type=["jpg", "jpeg", "png"])

    if image_url:
        st.image(image_url, caption="预览图片", width=300)
    elif uploaded_file:
        st.image(uploaded_file, caption="预览图片", width=300)

    question = st.text_input("你想问什么？", value="描述一下这张图片的内容")

    if st.button("开始分析"):
        if not image_url and not uploaded_file:
            st.warning("请提供图片")
            st.stop()

        # 处理图片 URL
        final_image_url = image_url
        if uploaded_file:
            import base64
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode()
            mime_type = uploaded_file.type
            final_image_url = f"data:{mime_type};base64,{base64_image}"

        # 调用后端的 /vision/analyze 接口
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                payload = {
                    "image_url": final_image_url,
                    "question": question,
                    "model": "deepseek-v4-flash-vision-exp"
                }
                response = requests.post(
                    f"{API_BASE_URL}/vision/analyze",
                    json=payload,
                    stream=True,
                    timeout=60
                )

                if response.status_code != 200:
                    st.error(f"后端返回错误: {response.status_code} - {response.text}")
                    st.stop()

                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确认 FastAPI 已启动")
            except Exception as e:
                st.error(f"图像分析失败: {e}")