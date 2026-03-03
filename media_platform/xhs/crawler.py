# -*- coding: utf-8 -*-
"""
小红书爬虫核心实现
参考 MediaCrawler 架构，基于 Playwright 实现
"""

import asyncio
import random
from typing import List, Dict, Optional
from playwright.async_api import BrowserContext

from base.base_crawler import AbstractCrawler
from base.browser_manager import BrowserManager
from config import settings
from .client import XHSClient
from .extractor import XHSExtractor


class XiaoHongShuCrawler(AbstractCrawler):
    """小红书爬虫 - Playwright 版"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser_manager: Optional[BrowserManager] = None
        self.client: Optional[XHSClient] = None
        self.context: Optional[BrowserContext] = None
        
    async def init(self):
        """初始化爬虫"""
        # 初始化浏览器
        self.browser_manager = BrowserManager(
            headless=self.headless,
            user_data_dir=settings.USER_DATA_DIR if settings.SAVE_LOGIN_STATE else None
        )
        self.context = await self.browser_manager.init_browser()
        
        # 初始化 API 客户端
        self.client = XHSClient(self.context)
        await self.client.init_session()
        
    async def start(self) -> None:
        """启动爬虫（用于自动运行）"""
        await self.init()
        
    async def search(self, keyword: str, max_notes: int = 20) -> List[Dict]:
        """搜索笔记"""
        all_notes = []
        page = 1
        page_size = settings.CRAWLER_CONFIG["page_size"]
        
        print(f"开始搜索关键词: {keyword}")
        
        while len(all_notes) < max_notes:
            print(f"获取第 {page} 页...")
            
            params = {
                'keyword': keyword,
                'page': page,
                'page_size': page_size,
                'sort': 'general',
                'note_type': 'all',
            }
            
            data = await self.client.request('GET', 'search/notes', params=params)
            
            if not data:
                print("没有更多数据")
                break
            
            items = data.get('items', [])
            if not items:
                break
            
            notes = XHSExtractor.extract_note_list(items)
            all_notes.extend(notes)
            
            print(f"已获取 {len(all_notes)}/{max_notes} 条笔记")
            
            # 随机延迟
            delay = settings.CRAWLER_CONFIG["sleep_sec"] + random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)
            
            page += 1
        
        return all_notes[:max_notes]
    
    async def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """获取笔记详情"""
        params = {'source_note_id': note_id}
        
        data = await self.client.request('GET', 'feed', params=params)
        
        if data:
            return XHSExtractor.extract_note_detail(data)
        return None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        params = {'user_id': user_id}
        
        data = await self.client.request('GET', 'user/other', params=params)
        
        if data:
            return XHSExtractor.extract_user_info(data)
        return None
    
    async def get_user_notes(self, user_id: str, max_notes: int = 20) -> List[Dict]:
        """获取用户发布的笔记"""
        all_notes = []
        page = 1
        page_size = settings.CRAWLER_CONFIG["page_size"]
        
        while len(all_notes) < max_notes:
            params = {
                'user_id': user_id,
                'page': page,
                'page_size': page_size,
            }
            
            data = await self.client.request('GET', 'user_posted', params=params)
            
            if not data:
                break
            
            notes = data.get('notes', [])
            if not notes:
                break
            
            parsed = XHSExtractor.extract_note_list(notes)
            all_notes.extend(parsed)
            
            delay = settings.CRAWLER_CONFIG["sleep_sec"] + random.uniform(0.5, 1.5)
            await asyncio.sleep(delay)
            
            page += 1
        
        return all_notes[:max_notes]
    
    async def close(self):
        """关闭爬虫"""
        if self.client:
            await self.client.close()
        if self.browser_manager:
            await self.browser_manager.close()
