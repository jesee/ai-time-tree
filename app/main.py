from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import json
from contextlib import asynccontextmanager

# 导入数据库、模型和 CRUD 操作
from app.core.database import engine, Base, get_db
from app.models import article
from app.crud import article as crud_article
# 导入调度器控制函数
from app.core.scheduler import start_scheduler, stop_scheduler

# 在应用启动时创建数据库表
Base.metadata.create_all(bind=engine)

# 使用 lifespan 事件处理器来管理后台任务
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行
    start_scheduler()
    yield
    # 应用关闭时执行
    stop_scheduler()

app = FastAPI(
    title="AI Time Tree",
    description="一个自动收集、总结并以时间轴展示最新AI资讯的项目。",
    version="0.1.0",
    lifespan=lifespan
)

# 挂载 static 文件夹，用于提供 CSS 和 JS 文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置 Jinja2 模板
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    提供前端主页面 index.html。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/articles")
def get_all_articles(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    API 端点，用于分页获取所有已处理并存储在数据库中的文章。
    - skip: 跳过的记录数
    - limit: 每页返回的记录数
    """
    articles = crud_article.get_articles(db, skip=skip, limit=limit)
    
    # 将 skills 字符串解析回 JSON 列表
    for art in articles:
        if art.skills:
            try:
                art.skills = json.loads(art.skills)
            except json.JSONDecodeError:
                art.skills = [] # 如果解析失败，提供一个空列表
        else:
            art.skills = [] # 确保前端总能收到一个列表
            
    return articles

@app.get("/api/health")
async def health_check():
    """
    健康检查端点。
    """
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
