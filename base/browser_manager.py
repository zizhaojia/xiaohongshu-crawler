# -*- coding: utf-8 -*-
"""
Playwright 浏览器管理器
负责浏览器生命周期管理和上下文维护
"""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self, headless: bool = False, user_data_dir: Optional[str] = None):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def init_browser(self) -> BrowserContext:
        """初始化浏览器"""
        self.playwright = await async_playwright().start()
        
        # 启动浏览器
        launch_kwargs = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        }
        
        try:
            self.browser = await self.playwright.chromium.launch(**launch_kwargs)
        except Exception as e:
            # 尝试使用系统 Chrome
            launch_kwargs["executable_path"] = "/usr/bin/google-chrome"
            self.browser = await self.playwright.chromium.launch(**launch_kwargs)
        
        # 创建上下文
        context_kwargs = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        
        if self.user_data_dir:
            # 使用持久化上下文保存登录态
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                **launch_kwargs,
                **context_kwargs
            )
        else:
            self.context = await self.browser.new_context(**context_kwargs)
        
        # 注入反检测脚本
        await self._inject_anti_detect()
        
        self.page = await self.context.new_page()
        return self.context
    
    async def _inject_anti_detect(self):
        """注入反检测脚本"""
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
    
    async def get_xhs_sign(self, api_url: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """
        获取小红书签名
        在浏览器环境中执行 JS 获取 x-s、x-t 等签名参数
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        # 访问小红书页面确保环境正确
        await self.page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        # 构造获取签名的 JS 代码
        js_code = """
            () => {
                return new Promise((resolve) => {
                    try {
                        // 小红书签名逻辑通常在 window._byted_acrawler 或类似对象
                        // 如果没有现成的，我们构造基本参数
                        const x_t = Date.now().toString();
                        
                        // 尝试获取签名函数
                        let sign = '';
                        if (window._byted_acrawler && window._byted_acrawler.sign) {
                            sign = window._byted_acrawler.sign(arguments[0]);
                        } else if (window.sign) {
                            sign = window.sign(arguments[0]);
                        } else {
                            // 备用方案：使用简单时间戳作为标识
                            sign = 'x' + Math.random().toString(36).substring(2, 15);
                        }
                        
                        resolve({
                            'x-t': x_t,
                            'x-s': sign,
                            'x-b3-traceid': x_t + Math.random().toString(36).substring(2, 10)
                        });
                    } catch (e) {
                        resolve({
                            'x-t': Date.now().toString(),
                            'x-s': 'error',
                            'error': e.message
                        });
                    }
                });
            }
        """
        
        try:
            result = await self.page.evaluate(js_code, {"url": api_url, "data": data})
            return result
        except Exception as e:
            # 返回基础时间戳
            import time
            return {
                'x-t': str(int(time.time() * 1000)),
                'x-s': 'fallback',
                'x-b3-traceid': str(int(time.time() * 1000))
            }
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
