import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import os

# 确保脚本可以找到 'scripts' 目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.run_pipeline import main_pipeline

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化调度器
scheduler = AsyncIOScheduler()

def schedule_pipeline_job():
    """
    定义并添加周期性执行数据管道的任务。
    """
    logging.info("正在设置定时任务：每天晚上 23:00 运行一次数据管道...")
    
    # 使用 CronTrigger 来设置每天固定的执行时间
    scheduler.add_job(
        main_pipeline,
        trigger=CronTrigger(hour=23, minute=0),
        id="pipeline_job",
        name="Run data pipeline every day at 23:00",
        replace_existing=True
    )

def start_scheduler():
    """启动调度器"""
    logging.info("启动后台定时任务调度器...")
    scheduler.start()

def stop_scheduler():
    """停止调度器"""
    logging.info("停止后台定时任务调度器...")
    scheduler.shutdown()

# 在模块加载时直接配置好任务
schedule_pipeline_job()
