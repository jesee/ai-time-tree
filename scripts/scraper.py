import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from urllib.parse import urljoin
import re

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 目标网站 URL
TARGET_URL = "https://www.aivi.fyi/"

def fetch_article_urls(base_url: str):
    """
    从 aivi.fyi 首页抓取最新的文章列表。
    返回一个包含标题、链接和摘要的字典列表。
    """
    logging.info(f"开始抓取文章列表: {base_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"抓取文章列表失败: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    article_items = soup.find_all('div', class_='list__item')
    
    articles = []
    if not article_items:
        logging.warning("未找到任何文章，可能是页面结构已改变。")
        return []

    logging.info(f"找到了 {len(article_items)} 篇文章。")

    for item in article_items:
        title_tag = item.find('h2', class_='archive__item-title').find('a')
        excerpt_tag = item.find('p', class_='archive__item-excerpt')
        
        if title_tag and excerpt_tag:
            title = title_tag.get_text(strip=True)
            relative_url = title_tag['href']
            absolute_url = urljoin(base_url, relative_url)
            excerpt = excerpt_tag.get_text(strip=True)
            
            articles.append({
                "title": title,
                "url": absolute_url,
                "summary_from_page": excerpt
            })
            
    return articles

def fetch_article_content(article_url: str):
    """
    抓取单篇文章的详细内容和发布日期。
    """
    logging.info(f"开始抓取文章内容: {article_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"抓取文章内容失败: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 正确的内容选择器
    content_section = soup.find('section', class_='page__content')
    if not content_section:
        logging.warning(f"在 {article_url} 未找到 class='page__content' 的内容区域。")
        return None
        
    paragraphs = content_section.find_all('p')
    content = "\n".join([p.get_text(strip=True) for p in paragraphs])

    # --- 正确的日期提取逻辑 ---
    # 优先使用用户提供的、最精确的选择器 <time class="dt-published">
    date_str = None
    time_tag = soup.find('time', class_='dt-published')
    if time_tag and 'datetime' in time_tag.attrs:
        date_str = time_tag['datetime']

    published_date = datetime.now() # 设置一个默认值
    if date_str:
        try:
            # fromisoformat 可以处理带时区信息的 ISO 8601 日期字符串
            published_date = datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            logging.warning(f"无法从 '{date_str}' 解析日期，将使用当前时间。")
    else:
        # 如果上面的方法失败了，再尝试从 meta 标签中寻找作为备用方案
        meta_tag = soup.find('meta', property='article:published_time')
        if meta_tag and 'content' in meta_tag.attrs:
            date_str = meta_tag['content']
            try:
                published_date = datetime.fromisoformat(date_str)
            except (ValueError, TypeError):
                logging.warning(f"无法从 meta 标签 '{date_str}' 解析日期，将使用当前时间。")
        else:
            logging.warning(f"在 {article_url} 未找到任何有效的发布日期，将使用当前时间。")

    return {
        "content": content,
        "published_date": published_date
    }

if __name__ == '__main__':
    logging.info("--- 开始测试最终版爬虫脚本 (aivi.fyi) ---")
    
    latest_articles = fetch_article_urls(TARGET_URL)
    if latest_articles:
        print(f"\n成功抓取到 {len(latest_articles)} 篇文章链接:")
        for i, article in enumerate(latest_articles[:3], 1):
            print(f"  {i}. 标题: {article['title']}")
            print(f"     链接: {article['url']}")
            
        first_article_url = latest_articles[0]['url']
        print(f"\n--- 开始测试抓取单篇文章内容: {first_article_url} ---")
        
        details = fetch_article_content(first_article_url)
        if details:
            print(f"\n成功抓取到内容:")
            print(f"  发布日期: {details['published_date']}")
            print(f"  内容预览: {details['content'][:200]}...")
        else:
            print("\n抓取单篇文章内容失败。")
    else:
        print("\n抓取文章列表失败。")
        
    logging.info("--- 爬虫脚本测试结束 ---")