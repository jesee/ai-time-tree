import logging
import sys
import os

# 将项目根目录添加到 Python 路径中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 从我们新的抽象层导入全局 AI 客户端实例
from app.core.ai_provider import ai_client
from app.core.config import is_config_valid

def summarize_article_with_ai(title: str, content: str):
    """
    使用配置好的通用 AI 客户端总结文章内容并提取技巧。
    """
    if not ai_client:
        logging.error("AI client is not initialized. Check configuration and errors on startup.")
        return None

    # 为避免超出 token 限制，对过长的文章内容进行截断
    max_length = 15000
    if len(content) > max_length:
        logging.warning(f"Content length ({len(content)}) is too long, truncating to {max_length} characters.")
        content = content[:max_length]

    prompt = f"""
    作为一名顶尖的中文AI技术分析师，你的任务是深入分析以下标题为《{title}》的前沿技术文章。
    请产出一个结构化的 JSON 对象，其中必须包含 "summary" 和 "skills" 两个键。

    1.  **"summary"**: (是什么，有什么用)
        请用简体中文撰写一段150-200字的专业摘要。摘要需清晰地阐述以下两点：
        - **这是什么 (What)**: 明确指出文章介绍的核心新技术、新框架或新模型是什么。
        - **它解决了什么问题 (Why)**: 精准说明这项新技术旨在解决什么痛点，或带来了什么样的核心价值与作用。

    2.  **"skills"**: (能给我们什么帮助)
        请提炼一个包含3到5个简体中文关键点的 JSON 数组。每个关键点都应是读者通过阅读文章可以获得的、具体的、可行动的帮助或启发，例如：
        - 一个可以直接应用的编程技巧或命令。
        - 一个解决特定问题的新思路或新方法。
        - 一个值得关注的开源工具或技术趋势。

    文章内容如下:
    ---
    {content}
    ---

    请严格按照以下 JSON 格式返回结果，确保所有文本都是简体中文:
    {{
      "summary": "...",
      "skills": [
        "关键点1：可直接应用的技巧或方法",
        "关键点2：值得关注的新工具或趋势",
        "关键点3：解决某个特定问题的新思路"
      ]
    }}
    """

    try:
        result = ai_client.generate_structured_output(prompt)

        # 简单的结果校验
        if result and "summary" in result and "skills" in result and isinstance(result["skills"], list):
            return result
        else:
            logging.error(f"AI response has incorrect JSON structure: {result}")
            return None
    except Exception as e:
        logging.error(f"An error occurred during AI summarization: {e}")
        return None

if __name__ == '__main__':
    logging.info("--- Testing the AI Summarizer Script with Generic Provider ---")
    
    if not is_config_valid or not ai_client:
        logging.error("AI configuration is invalid or client failed to initialize. Test aborted.")
        logging.error("Please ensure your .env file is correctly set up.")
    else:
        sample_title = "XYZ Framework: The Next Big Thing in Web Development"
        sample_content = (
            "The XYZ framework is a revolutionary tool designed to simplify web development. "
            "It uses a component-based architecture, greatly enhancing code reusability. "
            "One of its core features is 'live state binding', which automatically updates the UI "
            "based on data changes. Developers can also use its built-in CLI to quickly scaffold "
            "new projects. Getting started is as simple as running 'npm install xyz-framework'. "
            "The official documentation details best practices for state management and API integration, "
            "ensuring scalable applications."
        )

        print("\n--- Sending sample text for AI summarization ---")
        ai_result = summarize_article_with_ai(sample_title, sample_content)

        if ai_result:
            print("\n--- Successfully received and parsed AI response ---")
            print(f"\nSummary:\n{ai_result['summary']}")
            print("\nSkills/Takeaways:")
            for skill in ai_result['skills']:
                print(f"- {skill}")
        else:
            print("\n--- Failed to get a valid summary from the AI provider ---")