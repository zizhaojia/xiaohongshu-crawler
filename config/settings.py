# -*- coding: utf-8 -*-
"""
配置文件
"""

import os

# 基础配置
HEADLESS = False  # 是否无头模式
SAVE_LOGIN_STATE = True  # 是否保存登录状态
USER_DATA_DIR = "./browser_data"  # 浏览器数据目录

# 小红书配置
XHS_CONFIG = {
    "platform": "xhs",
    "base_url": "https://www.xiaohongshu.com",
    "api_prefix": "https://www.xiaohongshu.com/api/sns/web/v1",
    "sign_api": "https://www.xiaohongshu.com/api/sec/v1/sign",
}

# 爬取配置
CRAWLER_CONFIG = {
    "max_notes": 20,  # 默认最大笔记数
    "max_concurrency": 1,  # 最大并发数
    "sleep_sec": 2,  # 请求间隔(秒)
    "page_size": 20,  # 每页数量
}

# 存储配置
SAVE_CONFIG = {
    "data_dir": "./data",
    "format": "json",  # json, csv, excel
}

# 确保目录存在
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(SAVE_CONFIG["data_dir"], exist_ok=True)
