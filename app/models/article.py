from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Article(Base):
    """
    文章数据模型 (ORM Model)
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    title = Column(String(255), nullable=False, comment="文章标题")
    
    # 使用 unique=True 确保我们不会重复存储同一篇文章
    url = Column(String(512), unique=True, nullable=False, index=True, comment="原文链接")
    
    published_date = Column(DateTime, nullable=False, comment="发布日期")
    
    summary = Column(Text, nullable=True, comment="AI 生成的内容摘要")
    
    skills = Column(Text, nullable=True, comment="AI 提炼的技巧/能力点列表 (JSON 格式存储)")
    
    # default=func.now() 会在创建记录时自动设置为当前时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")

    def __repr__(self):
        return f"<Article(title='{self.title}', url='{self.url}')>"
