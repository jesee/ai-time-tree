# 使用官方的 Python 3.12 slim 镜像作为基础
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到镜像中
COPY requirements.txt .

# 安装依赖 (使用清华大学的国内镜像源加速)
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

# 将我们项目的所有文件复制到镜像的 /app 目录下
COPY . .

# 声明容器在运行时监听的端口
EXPOSE 8000

# 容器启动时要执行的命令
# 使用 uvicorn 启动 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
