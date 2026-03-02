# 小红书爬虫工具

## ⚠️ 重要声明

本工具仅供**学习研究**使用，请遵守以下规则：

1. **遵守法律法规**：爬取数据不得用于非法用途
2. **遵守平台规则**：不要频繁请求，避免对平台造成压力
3. **尊重隐私**：不要爬取和传播个人隐私信息
4. **免责声明**：使用本工具产生的任何法律问题，由使用者自行承担

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 获取 Cookie（重要）

小红书需要登录才能获取完整数据：

1. 打开浏览器，访问 https://www.xiaohongshu.com
2. 登录你的账号
3. 按 F12 打开开发者工具
4. 切换到 Network（网络）标签
5. 刷新页面，找到一个请求（如 `notes` 或 `feed`）
6. 在请求头中找到 `Cookie` 字段，复制整个值
7. 粘贴到代码中的 `cookie` 变量

### 3. 运行爬虫

```bash
python xiaohongshu_crawler.py
```

## 📖 使用示例

### 示例 1：按关键词搜索

```python
from xiaohongshu_crawler import XiaoHongShuCrawler

# 初始化（带Cookie）
crawler = XiaoHongShuCrawler(cookie="你的Cookie")

# 搜索关键词
notes = crawler.crawl_by_keyword(
    keyword="美食",      # 搜索关键词
    max_notes=50,        # 最多爬取50条
    delay=3.0            # 每次请求间隔3秒
)

# 打印结果
for note in notes:
    print(f"标题: {note['title']}")
    print(f"作者: {note['user']['nickname']}")
    print(f"点赞: {note['likes']}")
    print("---")
```

### 示例 2：获取笔记详情

```python
# 获取单条笔记详情
note_detail = crawler.get_note_detail("笔记ID")
print(json.dumps(note_detail, ensure_ascii=False, indent=2))
```

### 示例 3：获取用户信息

```python
# 获取用户信息
user_info = crawler.get_user_info("用户ID")
print(f"昵称: {user_info['nickname']}")
print(f"粉丝: {user_info['fans']}")
print(f"关注: {user_info['follows']}")
```

### 示例 4：获取用户发布的笔记

```python
# 获取用户的所有笔记
user_notes = crawler.get_user_notes(
    user_id="用户ID",
    page=1,
    page_size=20
)
```

## 📊 数据结构

### 笔记信息

```json
{
  "note_id": "笔记ID",
  "title": "笔记标题",
  "desc": "笔记正文",
  "type": "normal/video",
  "likes": 100,
  "comments": 20,
  "collects": 50,
  "share_count": 10,
  "publish_time": "2024-01-01 12:00:00",
  "images": ["图片URL1", "图片URL2"],
  "tags": ["标签1", "标签2"],
  "ip_location": "IP属地",
  "user": {
    "user_id": "用户ID",
    "nickname": "昵称",
    "avatar": "头像URL",
    "home_link": "主页链接"
  }
}
```

### 用户信息

```json
{
  "user_id": "用户ID",
  "nickname": "昵称",
  "avatar": "头像URL",
  "desc": "个人简介",
  "gender": 2,
  "follows": 100,
  "fans": 1000,
  "interaction": 5000,
  "note_count": 50,
  "collected_count": 100,
  "location": "地址",
  "home_link": "主页链接"
}
```

## ⚡ 进阶使用

### 保存到 Excel

```python
import pandas as pd
from xiaohongshu_crawler import XiaoHongShuCrawler

crawler = XiaoHongShuCrawler(cookie="你的Cookie")
notes = crawler.crawl_by_keyword("美食", max_notes=100)

# 转换为DataFrame
df = pd.DataFrame(notes)

# 展开用户信息
df['user_id'] = df['user'].apply(lambda x: x['user_id'])
df['user_nickname'] = df['user'].apply(lambda x: x['nickname'])

# 保存到Excel
df.to_excel('xiaohongshu_notes.xlsx', index=False, engine='openpyxl')
print("已保存到 xiaohongshu_notes.xlsx")
```

### 保存到数据库

```python
import sqlite3
import json
from xiaohongshu_crawler import XiaoHongShuCrawler

# 创建数据库连接
conn = sqlite3.connect('xiaohongshu.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        note_id TEXT PRIMARY KEY,
        title TEXT,
        desc TEXT,
        likes INTEGER,
        comments INTEGER,
        collects INTEGER,
        publish_time TEXT,
        user_id TEXT,
        user_nickname TEXT,
        data TEXT
    )
''')

# 爬取数据
crawler = XiaoHongShuCrawler(cookie="你的Cookie")
notes = crawler.crawl_by_keyword("美食", max_notes=100)

# 插入数据
for note in notes:
    cursor.execute('''
        INSERT OR REPLACE INTO notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        note['note_id'],
        note['title'],
        note['desc'],
        note['likes'],
        note['comments'],
        note['collects'],
        note['publish_time'],
        note['user']['user_id'],
        note['user']['nickname'],
        json.dumps(note, ensure_ascii=False)
    ))

conn.commit()
conn.close()
print("数据已保存到数据库")
```

## 🛡️ 反爬虫策略

小红书有多种反爬虫机制：

1. **请求频率限制**：过于频繁的请求会触发风控
2. **Cookie验证**：部分接口需要登录态
3. **IP限制**：同一IP大量请求会被封
4. **滑块验证**：异常行为会触发验证码

### 应对建议

1. **设置合理延迟**：每次请求间隔 2-5 秒
2. **使用代理池**：轮换 IP 避免被封
3. **模拟真实用户**：使用真实浏览器的 User-Agent
4. **控制爬取量**：单次不要爬取太多数据

### 代理示例

```python
import requests

proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080',
}

response = requests.get(url, proxies=proxies)
```

## 🔧 常见问题

### Q1: 为什么获取不到数据？

- 检查 Cookie 是否有效（是否过期）
- 检查是否触发反爬（尝试增加延迟）
- 部分接口可能需要特定权限

### Q2: Cookie 过期了怎么办？

- 重新登录小红书
- 按上述步骤重新复制 Cookie

### Q3: 爬取速度很慢？

- 这是正常的，为了避免被封，建议保持 2-5 秒间隔
- 如需加快速度，可以使用代理池

### Q4: 可以爬取评论吗？

- 当前版本暂未实现，后续可以添加
- 评论接口需要额外的认证

## 📜 更新日志

### v1.0.0 (2026-03-02)
- 基础爬虫功能
- 支持关键词搜索
- 支持笔记详情获取
- 支持用户信息获取

## 📞 联系

如有问题，请通过 GitHub Issues 反馈。

---

**再次提醒：请合法合规使用本工具！**
