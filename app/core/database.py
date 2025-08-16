import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 获取项目根目录
# /home/baby/www/service/zhishi-collect/app/core/database.py -> /home/baby/www/service/zhishi-collect
# os.path.dirname() 会返回当前文件所在的目录
# 我们需要三次 to get to the root from app/core/database.py
# 1. app/core
# 2. app
# 3. root
# 实际上，更稳健的方式是基于 main.py 的位置或使用环境变量
# 这里我们用一个简单的方式，假设我们的工作目录是项目根目录
# 在生产环境中，这个路径应该通过配置管理
# 在容器内，我们将把数据库文件放在 /app/data/ 目录下
DATABASE_URL = "sqlite:///./data/aiview.db"

# 创建 SQLAlchemy 引擎
# connect_args 是 SQLite 特有的配置，允许多个线程共享同一个连接
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建一个 SessionLocal 类，每个实例都将是一个数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个 Base 类，我们的 ORM 模型将继承这个类
Base = declarative_base()

def get_db():
    """
    FastAPI 依赖注入函数，用于获取数据库会话。
    它确保数据库会话在请求处理完毕后总是被关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
