# -*- coding: utf-8 -*-
"""
存储模块
"""

import json
import os
import csv
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime

from config import settings


class BaseStore(ABC):
    """存储基类"""
    
    @abstractmethod
    def save(self, data: List[Dict], filename: str) -> str:
        """保存数据"""
        pass


class JSONStore(BaseStore):
    """JSON 存储"""
    
    def save(self, data: List[Dict], filename: str) -> str:
        filepath = os.path.join(settings.SAVE_CONFIG["data_dir"], f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存: {filepath}")
        return filepath


class CSVStore(BaseStore):
    """CSV 存储"""
    
    def save(self, data: List[Dict], filename: str) -> str:
        if not data:
            return ""
        
        filepath = os.path.join(settings.SAVE_CONFIG["data_dir"], f"{filename}.csv")
        
        # 扁平化数据（处理嵌套的 user 对象）
        flat_data = []
        for item in data:
            flat_item = item.copy()
            
            # 处理 user 嵌套
            if 'user' in flat_item and isinstance(flat_item['user'], dict):
                user = flat_item.pop('user')
                flat_item['user_id'] = user.get('user_id', '')
                flat_item['user_nickname'] = user.get('nickname', '')
            
            # 处理列表字段（转换为字符串）
            for key, value in flat_item.items():
                if isinstance(value, list):
                    flat_item[key] = ', '.join(str(v) for v in value)
            
            flat_data.append(flat_item)
        
        # 写入 CSV
        keys = flat_data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(flat_data)
        
        print(f"数据已保存: {filepath}")
        return filepath


class DataStore:
    """数据存储管理器"""
    
    def __init__(self, store_type: str = "json"):
        self.store_type = store_type
        self.store = self._get_store()
    
    def _get_store(self) -> BaseStore:
        """获取存储实例"""
        if self.store_type == "csv":
            return CSVStore()
        return JSONStore()
    
    def save(self, data: List[Dict], prefix: str = "data") -> str:
        """保存数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}"
        return self.store.save(data, filename)
