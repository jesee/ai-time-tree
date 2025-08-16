from sqlalchemy.orm import Session
from app.models.article import Article
from datetime import datetime

def get_article_by_url(db: Session, url: str):
    """
    通过 URL 查询单篇文章。
    用于在插入新文章前检查是否已存在。
    """
    return db.query(Article).filter(Article.url == url).first()

def create_article(db: Session, title: str, url: str, published_date: datetime, summary: str, skills: str):
    """
    创建并保存一篇新文章。
    """
    db_article = Article(
        title=title,
        url=url,
        published_date=published_date,
        summary=summary,
        skills=skills
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    """
    获取文章列表，支持分页。
    按发布日期降序排序。
    """
    return db.query(Article).order_by(Article.published_date.desc()).offset(skip).limit(limit).all()
