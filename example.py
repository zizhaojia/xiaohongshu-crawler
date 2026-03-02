#!/usr/bin/env python3
"""
小红书爬虫使用示例
"""

from xiaohongshu_crawler import XiaoHongShuCrawler
import json
import pandas as pd
from datetime import datetime

def example_1_basic_search():
    """示例1: 基础搜索"""
    print("=" * 50)
    print("示例1: 基础搜索")
    print("=" * 50)
    
    # 不登录的方式（功能受限）
    crawler = XiaoHongShuCrawler()
    
    # 搜索关键词
    keyword = "美食"
    notes = crawler.search_notes(keyword, page=1, page_size=10)
    
    print(f"搜索关键词: {keyword}")
    print(f"获取到 {len(notes)} 条笔记\n")
    
    for i, note in enumerate(notes[:5], 1):
        print(f"[{i}] {note['title']}")
        print(f"    作者: {note['user']['nickname']}")
        print(f"    点赞: {note['likes']} | 评论: {note['comments']} | 收藏: {note['collects']}")
        print()


def example_2_with_cookie():
    """示例2: 使用Cookie获取完整数据"""
    print("=" * 50)
    print("示例2: 使用Cookie获取完整数据")
    print("=" * 50)
    
    # 请替换为你的Cookie
    cookie = ""  # <-- 在这里填入你的Cookie
    
    if not cookie:
        print("请先填入你的Cookie！")
        print("获取方法：登录小红书后，在浏览器开发者工具中复制Cookie")
        return
    
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 爬取更多数据
    keyword = "旅行"
    notes = crawler.crawl_by_keyword(
        keyword=keyword,
        max_notes=20,
        delay=3.0
    )
    
    # 保存为JSON
    filename = f'notes_{keyword}_{datetime.now().strftime("%Y%m%d")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {filename}")


def example_3_user_info():
    """示例3: 获取用户信息"""
    print("=" * 50)
    print("示例3: 获取用户信息")
    print("=" * 50)
    
    cookie = ""  # <-- 在这里填入你的Cookie
    
    if not cookie:
        print("请先填入你的Cookie！")
        return
    
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 替换为实际的用户ID
    user_id = ""  # <-- 在这里填入用户ID
    
    if not user_id:
        print("请先填入用户ID！")
        return
    
    user_info = crawler.get_user_info(user_id)
    
    if user_info:
        print(f"用户昵称: {user_info['nickname']}")
        print(f"粉丝数: {user_info['fans']}")
        print(f"关注数: {user_info['follows']}")
        print(f"笔记数: {user_info['note_count']}")
        print(f"个人简介: {user_info['desc']}")
    else:
        print("获取用户信息失败")


def example_4_save_to_excel():
    """示例4: 保存到Excel"""
    print("=" * 50)
    print("示例4: 保存到Excel")
    print("=" * 50)
    
    try:
        import pandas as pd
        from openpyxl import Workbook
    except ImportError:
        print("请先安装依赖: pip install pandas openpyxl")
        return
    
    cookie = ""  # <-- 在这里填入你的Cookie
    
    if not cookie:
        print("请先填入你的Cookie！")
        return
    
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 搜索多个关键词
    keywords = ["美食", "旅行", "穿搭"]
    all_notes = []
    
    for keyword in keywords:
        print(f"正在搜索: {keyword}")
        notes = crawler.crawl_by_keyword(keyword, max_notes=10, delay=3.0)
        
        for note in notes:
            note['search_keyword'] = keyword
        
        all_notes.extend(notes)
    
    # 转换为DataFrame
    df = pd.DataFrame(all_notes)
    
    # 提取用户信息
    df['user_id'] = df['user'].apply(lambda x: x.get('user_id', ''))
    df['user_nickname'] = df['user'].apply(lambda x: x.get('nickname', ''))
    df['user_home'] = df['user'].apply(lambda x: x.get('home_link', ''))
    
    # 选择需要的列
    columns = [
        'note_id', 'title', 'desc', 'type',
        'likes', 'comments', 'collects', 'share_count',
        'publish_time', 'ip_location', 'tags',
        'user_id', 'user_nickname', 'user_home',
        'search_keyword'
    ]
    
    df_export = df[columns]
    
    # 保存到Excel
    filename = f'xiaohongshu_data_{datetime.now().strftime("%Y%m%d")}.xlsx'
    df_export.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"数据已保存到: {filename}")
    print(f"共 {len(df_export)} 条记录")


def example_5_batch_user_notes():
    """示例5: 批量获取用户笔记"""
    print("=" * 50)
    print("示例5: 批量获取用户笔记")
    print("=" * 50)
    
    cookie = ""  # <-- 在这里填入你的Cookie
    
    if not cookie:
        print("请先填入你的Cookie！")
        return
    
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 用户ID列表
    user_ids = []  # <-- 在这里填入用户ID列表
    
    if not user_ids:
        print("请先填入用户ID列表！")
        return
    
    all_user_notes = []
    
    for user_id in user_ids:
        print(f"正在获取用户 {user_id} 的笔记...")
        notes = crawler.get_user_notes(user_id, page=1, page_size=20)
        all_user_notes.extend(notes)
        
        # 延迟
        import time
        time.sleep(3)
    
    # 保存
    filename = f'user_notes_{datetime.now().strftime("%Y%m%d")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_user_notes, f, ensure_ascii=False, indent=2)
    
    print(f"共获取 {len(all_user_notes)} 条笔记")
    print(f"数据已保存到: {filename}")


if __name__ == '__main__':
    print("小红书爬虫示例脚本")
    print("=" * 50)
    print()
    
    # 选择要运行的示例
    print("请选择要运行的示例:")
    print("1. 基础搜索（无需Cookie）")
    print("2. 使用Cookie获取完整数据")
    print("3. 获取用户信息")
    print("4. 保存到Excel")
    print("5. 批量获取用户笔记")
    print()
    
    # 默认运行示例1
    example_1_basic_search()
    
    print("\n提示: 其他示例需要在代码中填入Cookie后才能运行")
    print("请编辑此文件，在对应位置填入你的Cookie")
