# -*- coding: utf-8 -*-
"""
新版主入口 - 使用 Playwright 架构
"""

import asyncio
import argparse
from media_platform.xhs import XiaoHongShuCrawler
from store.base_store import DataStore


async def main():
    parser = argparse.ArgumentParser(description='小红书爬虫 - Playwright 版')
    parser.add_argument('--action', type=str, default='search', 
                       choices=['search', 'detail', 'user'],
                       help='操作类型: search(搜索), detail(笔记详情), user(用户信息)')
    parser.add_argument('--keyword', type=str, help='搜索关键词')
    parser.add_argument('--note-id', type=str, help='笔记ID')
    parser.add_argument('--user-id', type=str, help='用户ID')
    parser.add_argument('--max-notes', type=int, default=20, help='最大笔记数')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'csv'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    # 初始化爬虫
    crawler = XiaoHongShuCrawler(headless=args.headless)
    store = DataStore(store_type=args.format)
    
    try:
        await crawler.init()
        
        if args.action == 'search':
            if not args.keyword:
                print("请提供搜索关键词: --keyword")
                return
            
            results = await crawler.search(args.keyword, max_notes=args.max_notes)
            if results:
                store.save(results, f"search_{args.keyword}")
                print(f"共获取 {len(results)} 条笔记")
            
        elif args.action == 'detail':
            if not args.note_id:
                print("请提供笔记ID: --note-id")
                return
            
            result = await crawler.get_note_detail(args.note_id)
            if result:
                store.save([result], f"note_{args.note_id}")
                print(f"标题: {result.get('title', '')}")
        
        elif args.action == 'user':
            if not args.user_id:
                print("请提供用户ID: --user-id")
                return
            
            user_info = await crawler.get_user_info(args.user_id)
            if user_info:
                print(f"用户: {user_info.get('nickname', '')}")
                print(f"粉丝: {user_info.get('fans', 0)}")
                
                notes = await crawler.get_user_notes(args.user_id, max_notes=args.max_notes)
                if notes:
                    store.save(notes, f"user_notes_{args.user_id}")
                    print(f"共获取 {len(notes)} 条笔记")
    
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        await crawler.close()


if __name__ == '__main__':
    asyncio.run(main())
