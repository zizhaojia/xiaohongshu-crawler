# -*- coding: utf-8 -*-
"""
数据解析器 - 提取和格式化数据
"""

from typing import Dict, List, Any, Optional


class XHSExtractor:
    """小红书数据解析器"""
    
    @staticmethod
    def extract_note_list(items: List[Dict]) -> List[Dict]:
        """解析笔记列表"""
        result = []
        
        for item in items:
            try:
                note_card = item.get('note_card', item)  # 兼容不同结构
                
                parsed = {
                    'note_id': note_card.get('note_id', ''),
                    'title': note_card.get('title', ''),
                    'desc': note_card.get('desc', ''),
                    'type': note_card.get('type', 'normal'),  # normal: 图文, video: 视频
                    'likes': note_card.get('interact_info', {}).get('liked_count', 0),
                    'comments': note_card.get('interact_info', {}).get('comment_count', 0),
                    'collects': note_card.get('interact_info', {}).get('collected_count', 0),
                    'shares': note_card.get('interact_info', {}).get('share_count', 0),
                    'publish_time': note_card.get('time', ''),
                    'images': [img.get('url', '') for img in note_card.get('image_list', [])],
                    'video_url': note_card.get('video', {}).get('url', '') if note_card.get('type') == 'video' else '',
                    'tags': [tag.get('name', '') for tag in note_card.get('tag_list', [])],
                    'user': {
                        'user_id': note_card.get('user', {}).get('user_id', ''),
                        'nickname': note_card.get('user', {}).get('nickname', ''),
                        'avatar': note_card.get('user', {}).get('avatar', ''),
                    }
                }
                
                result.append(parsed)
                
            except Exception as e:
                print(f"解析笔记失败: {e}")
                continue
        
        return result
    
    @staticmethod
    def extract_note_detail(data: Dict) -> Optional[Dict]:
        """解析笔记详情"""
        try:
            note = data.get('note', data)
            
            return {
                'note_id': note.get('note_id', ''),
                'title': note.get('title', ''),
                'desc': note.get('desc', ''),
                'type': note.get('type', 'normal'),
                'likes': note.get('interact_info', {}).get('liked_count', 0),
                'comments': note.get('interact_info', {}).get('comment_count', 0),
                'collects': note.get('interact_info', {}).get('collected_count', 0),
                'shares': note.get('interact_info', {}).get('share_count', 0),
                'publish_time': note.get('time', ''),
                'images': [img.get('url', '') for img in note.get('image_list', [])],
                'video_url': note.get('video', {}).get('url', '') if note.get('type') == 'video' else '',
                'tags': [tag.get('name', '') for tag in note.get('tag_list', [])],
                'ip_location': note.get('ip_location', ''),
                'user': {
                    'user_id': note.get('user', {}).get('user_id', ''),
                    'nickname': note.get('user', {}).get('nickname', ''),
                    'avatar': note.get('user', {}).get('avatar', ''),
                }
            }
        except Exception as e:
            print(f"解析笔记详情失败: {e}")
            return None
    
    @staticmethod
    def extract_user_info(data: Dict) -> Optional[Dict]:
        """解析用户信息"""
        try:
            user = data.get('basic_info', data)
            
            return {
                'user_id': user.get('user_id', ''),
                'nickname': user.get('nickname', ''),
                'avatar': user.get('image', ''),
                'desc': user.get('desc', ''),
                'gender': user.get('gender', 0),  # 0: 未知, 1: 男, 2: 女
                'follows': user.get('follows', 0),
                'fans': user.get('fans', 0),
                'interaction': user.get('interaction', 0),
                'note_count': user.get('note_count', 0),
                'collected_count': user.get('collected_count', 0),
                'location': user.get('location', ''),
            }
        except Exception as e:
            print(f"解析用户信息失败: {e}")
            return None
