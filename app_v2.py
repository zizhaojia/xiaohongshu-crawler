# -*- coding: utf-8 -*-
"""
新版 Flask Web 界面 - 支持 Playwright 异步爬虫
"""

import asyncio
import json
import os
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, jsonify, send_file

from media_platform.xhs import XiaoHongShuCrawler
from store.base_store import DataStore

app = Flask(__name__)

# 存储目录
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# 全局状态
class CrawlerState:
    def __init__(self):
        self.is_crawling = False
        self.results = []
        self.message = ""

state = CrawlerState()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """搜索笔记 API"""
    if state.is_crawling:
        return jsonify({'success': False, 'message': '正在爬取中，请稍后'})
    
    data = request.json
    keyword = data.get('keyword', '').strip()
    max_notes = min(int(data.get('max_notes', 20)), 50)
    headless = data.get('headless', False)
    
    if not keyword:
        return jsonify({'success': False, 'message': '关键词不能为空'})
    
    # 在后台运行爬虫
    def run_crawler():
        state.is_crawling = True
        state.results = []
        state.message = f"开始搜索: {keyword}"
        
        async def do_crawl():
            crawler = XiaoHongShuCrawler(headless=headless)
            try:
                await crawler.init()
                results = await crawler.search(keyword, max_notes=max_notes)
                state.results = results
                state.message = f"搜索完成，共 {len(results)} 条笔记"
                
                # 自动保存
                store = DataStore()
                store.save(results, f"search_{keyword}")
                
            except Exception as e:
                state.message = f"爬取失败: {str(e)}"
            finally:
                await crawler.close()
                state.is_crawling = False
        
        asyncio.run(do_crawl())
    
    import threading
    thread = threading.Thread(target=run_crawler)
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': f'开始爬取关键词: {keyword}'
    })


@app.route('/api/status')
def get_status():
    """获取爬取状态"""
    return jsonify({
        'is_crawling': state.is_crawling,
        'message': state.message,
        'results_count': len(state.results)
    })


@app.route('/api/results')
def get_results():
    """获取爬取结果"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'total': len(state.results),
        'page': page,
        'per_page': per_page,
        'data': state.results[start:end]
    })


@app.route('/api/export/json')
def export_json():
    """导出 JSON"""
    if not state.results:
        return jsonify({'success': False, 'message': '没有数据可导出'})
    
    output = BytesIO()
    output.write(json.dumps(state.results, ensure_ascii=False, indent=2).encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'xhs_data_{datetime.now().strftime("%Y%m%d")}.json'
    )


@app.route('/api/export/csv')
def export_csv():
    """导出 CSV"""
    if not state.results:
        return jsonify({'success': False, 'message': '没有数据可导出'})
    
    store = DataStore(store_type='csv')
    filepath = store.save(state.results, f'xhs_export_{datetime.now().strftime("%Y%m%d")}')
    
    return send_file(
        filepath,
        mimetype='text/csv',
        as_attachment=True,
        download_name=os.path.basename(filepath)
    )


@app.route('/api/note/<note_id>')
def get_note_detail(note_id):
    """获取笔记详情"""
    headless = request.args.get('headless', 'false').lower() == 'true'
    
    async def fetch():
        crawler = XiaoHongShuCrawler(headless=headless)
        try:
            await crawler.init()
            result = await crawler.get_note_detail(note_id)
            return result
        finally:
            await crawler.close()
    
    try:
        result = asyncio.run(fetch())
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'success': False, 'message': '获取失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/user/<user_id>')
def get_user(user_id):
    """获取用户信息"""
    headless = request.args.get('headless', 'false').lower() == 'true'
    
    async def fetch():
        crawler = XiaoHongShuCrawler(headless=headless)
        try:
            await crawler.init()
            result = await crawler.get_user_info(user_id)
            return result
        finally:
            await crawler.close()
    
    try:
        result = asyncio.run(fetch())
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({'success': False, 'message': '获取失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
