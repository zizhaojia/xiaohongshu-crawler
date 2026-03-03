# -*- coding: utf-8 -*-
"""
小红书 API 客户端
基于 Playwright 环境发起请求，自动获取签名
"""

import asyncio
import aiohttp
from typing import Dict, Optional, Any
from playwright.async_api import BrowserContext


class XHSClient:
    """小红书 HTTP 客户端"""
    
    def __init__(self, context: BrowserContext, base_url: str = "https://www.xiaohongshu.com"):
        self.context = context
        self.base_url = base_url
        self.api_prefix = f"{base_url}/api/sns/web/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def init_session(self):
        """初始化 aiohttp session"""
        # 从 browser context 获取 cookies
        cookies = await self.context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        
        self.session = aiohttp.ClientSession(
            cookies=cookie_dict,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': 'https://www.xiaohongshu.com/',
                'Origin': 'https://www.xiaohongshu.com',
            }
        )
    
    async def get_sign(self, api_path: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """在浏览器中执行 JS 获取签名"""
        page = await self.context.new_page()
        try:
            # 访问小红书主页确保环境加载
            await page.goto("https://www.xiaohongshu.com", wait_until="networkidle")
            
            # 执行签名获取脚本
            sign_data = await page.evaluate("""
                async (apiPath) => {
                    return new Promise((resolve) => {
                        try {
                            const x_t = Date.now().toString();
                            
                            // 尝试调用小红书内部的签名函数
                            let x_s = '';
                            if (window._byted_acrawler && window._byted_acrawler.sign) {
                                x_s = window._byted_acrawler.sign(apiPath);
                            } else {
                                // 备用：生成伪签名
                                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                                for (let i = 0; i < 32; i++) {
                                    x_s += chars.charAt(Math.floor(Math.random() * chars.length));
                                }
                            }
                            
                            resolve({
                                'x-t': x_t,
                                'x-s': x_s,
                                'x-b3-traceid': x_t.substring(0, 16) + Math.random().toString(36).substring(2, 8)
                            });
                        } catch (e) {
                            resolve({'error': e.message});
                        }
                    });
                }
            """, api_path)
            
            return sign_data
        finally:
            await page.close()
    
    async def request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """发送 API 请求"""
        if not self.session:
            await self.init_session()
        
        url = f"{self.api_prefix}/{endpoint}"
        
        # 获取签名
        sign = await self.get_sign(endpoint, data)
        
        headers = {
            'x-t': sign.get('x-t', ''),
            'x-s': sign.get('x-s', ''),
            'x-b3-traceid': sign.get('x-b3-traceid', ''),
        }
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                **kwargs
            ) as response:
                result = await response.json()
                
                if result.get('success'):
                    return result.get('data', result)
                else:
                    print(f"API 错误: {result.get('msg', '未知错误')}")
                    return None
                    
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    async def close(self):
        """关闭 session"""
        if self.session:
            await self.session.close()
