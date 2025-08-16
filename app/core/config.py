import os
from dotenv import load_dotenv
import logging

# 定位并加载 .env 文件
# 这使得无论从哪里运行脚本，都能找到项目根目录下的 .env 文件
project_dir = os.path.join(os.path.dirname(__file__), '..', '..')
load_dotenv(os.path.join(project_dir, '.env'))

# 从环境变量中获取配置
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# --- Gemini Specific ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-latest")

# --- OpenAI Specific ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1") # Default to official API
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-4o")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_config():
    """检查关键配置是否存在"""
    logging.info(f"Selected AI Provider: {AI_PROVIDER}")
    if AI_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            logging.error("错误: AI_PROVIDER is 'gemini' but GEMINI_API_KEY is not set in .env.")
            return False
        logging.info(f"Using Gemini Model: {GEMINI_MODEL_ID}")
    elif AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            logging.error("Error: AI_PROVIDER is 'openai' but OPENAI_API_KEY is not set in .env.")
            return False
        logging.info(f"Using OpenAI Model: {OPENAI_MODEL_ID}")
        logging.info(f"Using OpenAI API Base: {OPENAI_API_BASE}")
    
    logging.info("Configuration loaded successfully.")
    return True

# 在模块加载时执行验证
is_config_valid = validate_config()
