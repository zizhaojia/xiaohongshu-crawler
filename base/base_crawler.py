# -*- coding: utf-8 -*-
"""
小红书爬虫重构版 - 参考 MediaCrawler 架构
核心改进：使用 Playwright 获取签名，无需 JS 逆向
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AbstractCrawler(ABC):
    """爬虫抽象基类"""
    
    @abstractmethod
    async def start(self) -> None:
        """启动爬虫"""
        pass
    
    @abstractmethod
    async def search(self, keyword: str, max_notes: int = 20) -> list:
        """搜索笔记"""
        pass
    
    @abstractmethod
    async def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """获取笔记详情"""
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        pass
    
    @abstractmethod
    async def get_user_notes(self, user_id: str, max_notes: int = 20) -> list:
        """获取用户笔记"""
        pass
