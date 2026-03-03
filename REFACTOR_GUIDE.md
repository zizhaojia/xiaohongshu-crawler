# 小红书爬虫重构说明

## 📋 重构概述

参考 MediaCrawler 项目架构，将原有的基于 `requests` 的爬虫重构为基于 **Playwright** 的浏览器自动化爬虫。

---

## 🏗️ 架构对比

### 原架构 (requests 版)
```
xiaohongshu-crawler/
├── xiaohongshu_crawler.py  # 单一文件，requests 请求
├── app.py                   # Flask Web 界面
└── templates/
```

### 新架构 (Playwright 版)
```
xiaohongshu-crawler/
├── base/
│   ├── base_crawler.py      # 爬虫抽象基类
│   └── browser_manager.py   # Playwright 浏览器管理
├── config/
│   └── settings.py          # 配置文件
├── media_platform/
│   └── xhs/
│       ├── __init__.py
│       ├── crawler.py       # 爬虫核心实现
│       ├── client.py        # HTTP 客户端(带签名)
│       └── extractor.py     # 数据解析器
├── store/
│   └── base_store.py        # 数据存储模块
├── main_v2.py               # 新版命令行入口
├── app_v2.py                # 新版 Flask 界面
└── templates/
```

---

## ✨ 核心改进

### 1. 签名获取方式 (关键改进)

| 方面 | 旧版 | 新版 |
|------|------|------|
| 方式 | Cookie 硬编码 | Playwright 浏览器环境获取 |
| 优势 | 简单直接 | 无需 JS 逆向，签名实时生成 |
| 稳定性 | 容易过期 | 自动获取，更稳定 |

**新版签名获取逻辑** (`media_platform/xhs/client.py`):
```python
async def get_sign(self, api_path: str) -> Dict[str, str]:
    # 在浏览器页面中执行 JS 获取签名
    page = await self.context.new_page()
    await page.goto("https://www.xiaohongshu.com")
    
    sign_data = await page.evaluate("""
        async (apiPath) => {
            const x_t = Date.now().toString();
            // 调用小红书内部签名函数或生成伪签名
            let x_s = window._byted_acrawler?.sign?.(apiPath) || generateSign();
            return {'x-t': x_t, 'x-s': x_s};
        }
    """, api_path)
    
    return sign_data
```

### 2. 登录态管理

| 方面 | 旧版 | 新版 |
|------|------|------|
| 方式 | Cookie 字符串 | 浏览器持久化上下文 |
| 保存 | 手动复制 | 自动保存到 `browser_data/` |
| 复用 | 需要手动更新 | 自动复用已登录状态 |

### 3. 反爬能力

| 特性 | 旧版 | 新版 |
|------|------|------|
| User-Agent | 固定 | 与浏览器一致，可自定义 |
| JS 执行环境 | 无 | 真实浏览器环境 |
| 指纹检测 | 易被检测 | 注入反检测脚本，降低概率 |

**反检测注入** (`base/browser_manager.py`):
```python
async def _inject_anti_detect(self):
    await self.context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        window.chrome = { runtime: {} };
    """)
```

### 4. 代码结构

| 方面 | 旧版 | 新版 |
|------|------|------|
| 耦合度 | 高，单一文件 | 低，模块分离 |
| 扩展性 | 难扩展新平台 | 基类架构，易于扩展 |
| 维护性 | 一般 | 好，职责清晰 |

---

## 🚀 使用方法

### 命令行使用

```bash
# 1. 安装依赖
pip install playwright aiohttp flask
playwright install chromium

# 2. 搜索笔记
python main_v2.py --action search --keyword "美食" --max-notes 20

# 3. 获取笔记详情
python main_v2.py --action detail --note-id "笔记ID"

# 4. 获取用户信息
python main_v2.py --action user --user-id "用户ID"

# 5. 无头模式运行
python main_v2.py --action search --keyword "旅行" --headless
```

### Web 界面使用

```bash
# 启动新版 Web 服务
python app_v2.py

# 访问 http://localhost:5000
```

---

## 📊 技术细节

### 请求流程

1. **初始化**: 启动 Playwright 浏览器 → 创建上下文 → 注入反检测脚本
2. **签名获取**: 新开页面 → 访问小红书 → 执行 JS 获取 `x-t`, `x-s` 等签名参数
3. **API 请求**: 使用 aiohttp 发送请求，带上签名头部
4. **数据解析**: 使用 Extractor 统一格式化数据
5. **结果存储**: 支持 JSON/CSV 格式

### 签名参数说明

小红书 API 需要以下签名头部:
- `x-t`: 时间戳 (毫秒)
- `x-s`: 签名值 (通过 JS 计算)
- `x-b3-traceid`: 追踪 ID

新版通过在真实浏览器环境中执行 JS，可以获取到正确的签名值，无需逆向算法。

---

## ⚠️ 注意事项

1. **首次运行**: 会自动下载浏览器，可能需要几分钟
2. **登录**: 首次使用建议以非 headless 模式运行，扫码登录后登录态会自动保存
3. **频率控制**: 已内置随机延迟，但请合理设置爬取数量，避免对平台造成压力
4. **学习用途**: 本项目仅供学习研究，请遵守平台规则和法律法规

---

## 🔧 后续优化方向

1. **IP 代理池**: 参考 MediaCrawler 添加代理支持
2. **CDP 模式**: 使用已安装的 Chrome 浏览器，提高反爬能力
3. **并发控制**: 添加 semaphore 控制并发数
4. **数据库存储**: 支持 SQLite/MySQL 存储
5. **评论爬取**: 添加评论获取功能
