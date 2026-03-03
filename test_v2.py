# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证新版爬虫架构
"""

import asyncio
from media_platform.xhs import XiaoHongShuCrawler


async def test_browser():
    """测试浏览器初始化"""
    print("=" * 50)
    print("测试1: 浏览器初始化")
    print("=" * 50)
    
    crawler = XiaoHongShuCrawler(headless=False)
    try:
        await crawler.init()
        print("✅ 浏览器初始化成功")
        
        # 测试访问小红书
        page = await crawler.context.new_page()
        await page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded")
        print("✅ 成功访问小红书首页")
        await page.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await crawler.close()


async def test_search():
    """测试搜索功能"""
    print("\n" + "=" * 50)
    print("测试2: 搜索功能")
    print("=" * 50)
    
    crawler = XiaoHongShuCrawler(headless=False)
    try:
        await crawler.init()
        print("正在搜索: 美食...")
        
        results = await crawler.search("美食", max_notes=5)
        
        if results:
            print(f"✅ 搜索成功，获取 {len(results)} 条笔记")
            print(f"\n第一条笔记:")
            print(f"  标题: {results[0].get('title', 'N/A')}")
            print(f"  作者: {results[0].get('user', {}).get('nickname', 'N/A')}")
            print(f"  点赞: {results[0].get('likes', 0)}")
        else:
            print("⚠️ 未获取到数据")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await crawler.close()


async def test_storage():
    """测试存储功能"""
    print("\n" + "=" * 50)
    print("测试3: 数据存储")
    print("=" * 50)
    
    from store.base_store import DataStore
    
    test_data = [
        {'note_id': '1', 'title': '测试笔记1', 'likes': 100},
        {'note_id': '2', 'title': '测试笔记2', 'likes': 200},
    ]
    
    # 测试 JSON 存储
    json_store = DataStore(store_type='json')
    filepath = json_store.save(test_data, 'test_json')
    print(f"✅ JSON 保存成功: {filepath}")
    
    # 测试 CSV 存储
    csv_store = DataStore(store_type='csv')
    filepath = csv_store.save(test_data, 'test_csv')
    print(f"✅ CSV 保存成功: {filepath}")


async def main():
    """运行所有测试"""
    print("小红书爬虫重构版测试")
    print("本测试将验证新架构的各项功能")
    print("请确保已安装: pip install playwright aiohttp")
    print("且已运行: playwright install chromium")
    
    try:
        # 选择测试项
        print("\n请选择测试项:")
        print("1. 浏览器初始化")
        print("2. 搜索功能 (需要小红书登录态)")
        print("3. 数据存储")
        print("4. 全部测试")
        
        choice = input("\n输入选项 (1-4): ").strip()
        
        if choice == '1':
            await test_browser()
        elif choice == '2':
            await test_search()
        elif choice == '3':
            await test_storage()
        elif choice == '4':
            await test_browser()
            await test_storage()
            await test_search()
        else:
            print("无效选项")
            
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
