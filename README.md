🤖 智能聊天机器人 · 前端
基于 Streamlit 的 Web 聊天界面，提供多轮对话、模型切换、提示词策略选择、流式输出和图像理解功能。

📖 项目简介
这是一个轻量级聊天机器人前端，使用 Streamlit 构建交互界面。用户可以通过侧边栏选择模型来源和提示词策略，在对话标签页中与 AI 实时聊天，在图像理解标签页中分析图片。

前端通过 HTTP 请求与 API 服务通信（默认地址 http://localhost:8000），所有模型推理和业务逻辑均由该服务处理。

✨ 功能特性
1. 模型选择
侧边栏切换 本地 Ollama 或 云端 DeepSeek

本地模型：llama3.2:3b、qwen2.5:7b、mistral、gemma2:9b

云端模型：deepseek-chat、deepseek-v4-flash-vision-exp

2. 提示词策略（可多选叠加）
策略	说明
Zero-shot	直接提问，不给示例
Few-shot	提供示例引导模型（可选情感分析 / 问答场景）
CoT	让模型一步步推理（可自定义任务描述）
Structured	强制 JSON 格式返回
3. 多轮对话与流式输出
基于 st.session_state 保存聊天历史

逐字显示 AI 回复，打字机效果

一键清空对话历史

4. 图像理解
支持图片 URL 或本地上传（jpg/jpeg/png）

自动 Base64 编码后发送给 API 服务

需要配置 DEEPSEEK_API_KEY

5. 界面细节
输入框固定在页面底部

标签页切换：对话 / 图像理解

🛠️ 技术栈
技术	用途
Streamlit	构建 Web 交互界面
requests	发送 HTTP 请求
python-dotenv	读取 .env 环境变量
🚀 快速开始
1. 安装依赖
bash
pip install streamlit requests python-dotenv
2. 配置环境变量
在项目根目录创建 .env 文件：

env
DEEPSEEK_API_KEY=sk-你的密钥
仅在使用云端 DeepSeek 或图像理解功能时需要。

3. 启动前端
bash
streamlit run app.py
访问 http://localhost:8501 即可使用。

运行前请确保 API 服务已启动在 http://localhost:8000，否则会提示“无法连接到后端服务”。

📂 项目结构
text
.
├── app.py              # Streamlit 前端主程序
├── .env                # 环境变量（需自行创建）
└── README.md
🎮 使用说明
侧边栏
模型来源：本地 Ollama / 云端 DeepSeek

模型选择：根据来源显示不同选项

提示词策略：可多选，Few-shot 和 CoT 有额外参数

清空对话历史：重置当前会话

对话标签页
底部输入框输入问题，回车发送

消息以气泡形式展示，AI 回复流式更新

图像理解标签页
选择图片 URL 或上传本地图片

输入问题，点击“开始分析”

需要 DEEPSEEK_API_KEY

⚠️ 注意事项
API 服务：本前端依赖运行在 http://localhost:8000 的 API 服务，请先启动该服务。

Ollama 服务：使用本地模式前，确保 Ollama 已运行（ollama serve）并拉取所需模型。

DeepSeek API Key：云端对话和图像理解均需在 .env 中配置。

端口：前端默认 8501，API 服务默认 8000，如有冲突请修改 app.py 中的 API_BASE_URL。

提示词模板：由 API 服务管理，前端仅传递策略参数。

📄 许可证
仅供学习交流使用。