PyCharm 调试指南 —— 前端（Streamlit）
本项目前端使用 Streamlit 构建，运行在独立进程中，需要单独配置调试。

一、前端调试（Streamlit）
配置 Debug
打开 Edit Configurations...

点击 + → Python

配置如下：

字段	值
Name	Streamlit Debug
Execution	Module name
Module name	streamlit
Parameters	run app.py
Working directory	项目根目录
Python interpreter	你的项目虚拟环境（如 ChattingTest）
开始调试
在 app.py 的 if prompt := st.chat_input(...): 处打断点

点击 🐞 Debug 启动

浏览器访问 http://localhost:8501

输入消息发送，前端会自动停在断点处

二、常见问题
问题	解决方案
断点为空心圆	检查解释器是否选对，重新打断点
前端断点不触发	确认配置了 Streamlit Debug 并用 Debug 启动
ModuleNotFoundError	确认虚拟环境已安装所有依赖（streamlit、requests、python-dotenv）
端口被占用	修改端口参数，例如 run app.py --server.port 8502
无法连接到后端服务	确认后端 API 已启动在 http://localhost:8000，或修改 app.py 中的 API_BASE_URL