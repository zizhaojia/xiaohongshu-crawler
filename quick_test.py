#!/usr/bin/env python3
"""
小红书爬虫快速测试脚本
"""

from xiaohongshu_crawler import XiaoHongShuCrawler
import json

def main():
    print("🍠 小红书爬虫快速测试")
    print("=" * 50)
    
    # 询问是否使用Cookie
    use_cookie = input("是否使用Cookie? (y/n): ").lower() == 'y'
    
    cookie = None
    if use_cookie:
        cookie = input("请输入Cookie: ").strip()
    
    # 初始化爬虫
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 输入关键词
    keyword = input("请输入搜索关键词: ").strip()
    
    if not keyword:
        print("关键词不能为空！")
        return
    
    # 输入数量
    try:
        max_notes = int(input("要爬取多少条笔记? (默认10): ") or "10")
    except:
        max_notes = 10
    
    print(f"\n开始搜索: {keyword}")
    print(f"计划获取: {max_notes} 条笔记")
    print("-" * 50)
    
    # 开始爬取
    if use_cookie:
        notes = crawler.crawl_by_keyword(keyword, max_notes=max_notes, delay=3.0)
    else:
        # 不使用Cookie，只能获取一页
        notes = crawler.search_notes(keyword, page=1, page_size=max_notes)
    
    print(f"\n✅ 成功获取 {len(notes)} 条笔记\n")
    
    # 显示结果
    print("📋 结果预览:")
    print("-" * 50)
    
    for i, note in enumerate(notes[:5], 1):
        print(f"\n[{i}] {note['title'][:50]}...")
        print(f"    作者: {note['user']['nickname']}")
        print(f"    点赞: {note['likes']} | 评论: {note['comments']} | 收藏: {note['collects']}")
        print(f"    链接: {note['user']['home_link']}")
    
    # 保存结果
    if notes:
        filename = f"{keyword}_notes.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        print(f"\n💾 完整结果已保存到: {filename}")
    
    print("\n✨ 测试完成！")

if __name__ == '__main__':
    main()
