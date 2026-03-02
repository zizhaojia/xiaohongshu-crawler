from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import threading
from datetime import datetime
from xiaohongshu_crawler import XiaoHongShuCrawler
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# 存储爬取结果
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# 全局爬虫实例
crawler = None
is_crawling = False
crawl_results = []

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """搜索笔记 API"""
    global is_crawling, crawl_results
    
    if is_crawling:
        return jsonify({'success': False, 'message': '正在爬取中，请稍后'})
    
    data = request.json
    keyword = data.get('keyword', '').strip()
    max_notes = min(int(data.get('max_notes', 10)), 50)  # 限制最大50条
    cookie = data.get('cookie', '').strip()
    
    if not keyword:
        return jsonify({'success': False, 'message': '关键词不能为空'})
    
    # 在后台线程中运行爬虫
    def do_crawl():
        global is_crawling, crawl_results
        is_crawling = True
        crawl_results = []
        
        try:
            crawler = XiaoHongShuCrawler(cookie=cookie if cookie else None)
            
            if cookie:
                crawl_results = crawler.crawl_by_keyword(keyword, max_notes=max_notes, delay=2.0)
            else:
                crawl_results = crawler.search_notes(keyword, page=1, page_size=max_notes)
            
            # 保存到文件
            filename = f"{DATA_DIR}/search_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(crawl_results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"爬取失败: {e}")
        finally:
            is_crawling = False
    
    thread = threading.Thread(target=do_crawl)
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': f'开始爬取关键词: {keyword}，预计获取 {max_notes} 条笔记'
    })

@app.route('/api/status')
def status():
    """获取爬取状态"""
    return jsonify({
        'is_crawling': is_crawling,
        'results_count': len(crawl_results)
    })

@app.route('/api/results')
def results():
    """获取爬取结果"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'total': len(crawl_results),
        'page': page,
        'per_page': per_page,
        'data': crawl_results[start:end]
    })

@app.route('/api/export/json')
def export_json():
    """导出 JSON"""
    if not crawl_results:
        return jsonify({'success': False, 'message': '没有数据可导出'})
    
    output = BytesIO()
    output.write(json.dumps(crawl_results, ensure_ascii=False, indent=2).encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'xiaohongshu_data_{datetime.now().strftime("%Y%m%d")}.json'
    )

@app.route('/api/export/excel')
def export_excel():
    """导出 Excel"""
    if not crawl_results:
        return jsonify({'success': False, 'message': '没有数据可导出'})
    
    try:
        df = pd.DataFrame(crawl_results)
        
        # 提取用户信息
        if 'user' in df.columns:
            df['user_id'] = df['user'].apply(lambda x: x.get('user_id', '') if isinstance(x, dict) else '')
            df['user_nickname'] = df['user'].apply(lambda x: x.get('nickname', '') if isinstance(x, dict) else '')
            df['user_home'] = df['user'].apply(lambda x: x.get('home_link', '') if isinstance(x, dict) else '')
        
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'xiaohongshu_data_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'})

@app.route('/api/user/<user_id>')
def get_user(user_id):
    """获取用户信息"""
    cookie = request.args.get('cookie', '').strip()
    
    try:
        crawler = XiaoHongShuCrawler(cookie=cookie if cookie else None)
        user_info = crawler.get_user_info(user_id)
        
        if user_info:
            return jsonify({'success': True, 'data': user_info})
        else:
            return jsonify({'success': False, 'message': '获取用户信息失败，可能需要Cookie'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'请求失败: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
