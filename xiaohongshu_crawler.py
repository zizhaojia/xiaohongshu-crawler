import requests
import time
import json
import re
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
import random

class XiaoHongShuCrawler:
    """
    小红书爬虫 - 仅供学习研究使用
    
    注意：
    1. 请遵守小红书平台规则和当地法律法规
    2. 爬取频率不宜过高，建议设置合理延迟
    3. 部分接口需要登录态（cookie）
    """
    
    def __init__(self, cookie: str = None):
        self.cookie = cookie
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
        }
        
        if cookie:
            self.headers['Cookie'] = cookie
            self.session.headers.update(self.headers)
    
    def search_notes(self, keyword: str, page: int = 1, page_size: int = 20) -> List[Dict]:
        """
        搜索笔记
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            笔记列表
        """
        url = 'https://www.xiaohongshu.com/api/sns/web/v1/search/notes'
        
        # 构造搜索参数
        params = {
            'keyword': keyword,
            'page': page,
            'page_size': page_size,
            'sort': 'general',  # general: 综合, time_descending: 最新
            'note_type': 'all',  # all: 全部, video: 视频, normal: 图文
        }
        
        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                notes = data.get('data', {}).get('items', [])
                return self._parse_notes(notes)
            else:
                print(f"搜索失败: {data.get('msg', '未知错误')}")
                return []
                
        except Exception as e:
            print(f"请求异常: {e}")
            return []
    
    def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记详情
        """
        url = f'https://www.xiaohongshu.com/api/sns/web/v1/feed'
        
        params = {
            'source_note_id': note_id,
        }
        
        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                return self._parse_note_detail(data.get('data', {}))
            else:
                print(f"获取详情失败: {data.get('msg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息
        """
        url = f'https://www.xiaohongshu.com/api/sns/web/v1/user/other'
        
        params = {
            'user_id': user_id,
        }
        
        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                return self._parse_user_info(data.get('data', {}))
            else:
                print(f"获取用户信息失败: {data.get('msg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    def get_user_notes(self, user_id: str, page: int = 1, page_size: int = 20) -> List[Dict]:
        """
        获取用户发布的笔记
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            笔记列表
        """
        url = 'https://www.xiaohongshu.com/api/sns/web/v1/user_posted'
        
        params = {
            'user_id': user_id,
            'page': page,
            'page_size': page_size,
        }
        
        try:
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                notes = data.get('data', {}).get('notes', [])
                return self._parse_notes(notes)
            else:
                print(f"获取用户笔记失败: {data.get('msg', '未知错误')}")
                return []
                
        except Exception as e:
            print(f"请求异常: {e}")
            return []
    
    def _parse_notes(self, notes: List[Dict]) -> List[Dict]:
        """解析笔记列表"""
        result = []
        
        for note in notes:
            try:
                note_card = note.get('note_card', {})
                
                parsed_note = {
                    'note_id': note_card.get('note_id', ''),
                    'title': note_card.get('title', ''),
                    'desc': note_card.get('desc', ''),
                    'type': note_card.get('type', ''),  # normal: 图文, video: 视频
                    'likes': note_card.get('interact_info', {}).get('liked_count', 0),
                    'comments': note_card.get('interact_info', {}).get('comment_count', 0),
                    'collects': note_card.get('interact_info', {}).get('collected_count', 0),
                    'share_count': note_card.get('interact_info', {}).get('share_count', 0),
                    'publish_time': note_card.get('time', ''),
                    'images': [img.get('url', '') for img in note_card.get('image_list', [])],
                    'tags': [tag.get('name', '') for tag in note_card.get('tag_list', [])],
                    'user': {
                        'user_id': note_card.get('user', {}).get('user_id', ''),
                        'nickname': note_card.get('user', {}).get('nickname', ''),
                        'avatar': note_card.get('user', {}).get('avatar', ''),
                        'home_link': f"https://www.xiaohongshu.com/user/profile/{note_card.get('user', {}).get('user_id', '')}",
                    }
                }
                
                result.append(parsed_note)
                
            except Exception as e:
                print(f"解析笔记失败: {e}")
                continue
        
        return result
    
    def _parse_note_detail(self, data: Dict) -> Dict:
        """解析笔记详情"""
        note = data.get('note', {})
        
        return {
            'note_id': note.get('note_id', ''),
            'title': note.get('title', ''),
            'desc': note.get('desc', ''),
            'type': note.get('type', ''),
            'likes': note.get('interact_info', {}).get('liked_count', 0),
            'comments': note.get('interact_info', {}).get('comment_count', 0),
            'collects': note.get('interact_info', {}).get('collected_count', 0),
            'share_count': note.get('interact_info', {}).get('share_count', 0),
            'publish_time': note.get('time', ''),
            'images': [img.get('url', '') for img in note.get('image_list', [])],
            'tags': [tag.get('name', '') for tag in note.get('tag_list', [])],
            'ip_location': note.get('ip_location', ''),
            'user': {
                'user_id': note.get('user', {}).get('user_id', ''),
                'nickname': note.get('user', {}).get('nickname', ''),
                'avatar': note.get('user', {}).get('avatar', ''),
                'home_link': f"https://www.xiaohongshu.com/user/profile/{note.get('user', {}).get('user_id', '')}",
            }
        }
    
    def _parse_user_info(self, data: Dict) -> Dict:
        """解析用户信息"""
        user = data.get('basic_info', {})
        
        return {
            'user_id': user.get('user_id', ''),
            'nickname': user.get('nickname', ''),
            'avatar': user.get('image', ''),
            'desc': user.get('desc', ''),
            'gender': user.get('gender', ''),  # 0: 未知, 1: 男, 2: 女
            'follows': user.get('follows', 0),
            'fans': user.get('fans', 0),
            'interaction': user.get('interaction', 0),
            'note_count': user.get('note_count', 0),
            'collected_count': user.get('collected_count', 0),
            'location': user.get('location', ''),
            'home_link': f"https://www.xiaohongshu.com/user/profile/{user.get('user_id', '')}",
        }
    
    def crawl_by_keyword(self, keyword: str, max_notes: int = 50, delay: float = 2.0) -> List[Dict]:
        """
        根据关键词爬取笔记（带自动翻页）
        
        Args:
            keyword: 搜索关键词
            max_notes: 最大爬取数量
            delay: 请求间隔（秒）
            
        Returns:
            笔记列表
        """
        all_notes = []
        page = 1
        page_size = 20
        
        print(f"开始爬取关键词: {keyword}")
        
        while len(all_notes) < max_notes:
            print(f"正在获取第 {page} 页...")
            
            notes = self.search_notes(keyword, page=page, page_size=page_size)
            
            if not notes:
                print("没有更多数据了")
                break
            
            all_notes.extend(notes)
            print(f"已获取 {len(all_notes)} 条笔记")
            
            # 随机延迟，避免被反爬
            sleep_time = delay + random.uniform(0.5, 1.5)
            print(f"等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)
            
            page += 1
        
        print(f"爬取完成，共 {len(all_notes)} 条笔记")
        return all_notes[:max_notes]


if __name__ == '__main__':
    # 使用示例
    
    # 方式1: 不登录（功能受限，可能无法获取完整数据）
    # crawler = XiaoHongShuCrawler()
    
    # 方式2: 使用Cookie登录（推荐）
    # 从浏览器开发者工具复制 Cookie
    cookie = "你的小红书Cookie"
    crawler = XiaoHongShuCrawler(cookie=cookie)
    
    # 按关键词搜索
    keyword = "美食"
    notes = crawler.crawl_by_keyword(keyword, max_notes=10, delay=3.0)
    
    # 保存结果
    with open(f'notes_{keyword}.json', 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到 notes_{keyword}.json")
