#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EC商品ページ自動作成システム - 基本バージョン
ASINからAmazon商品情報を取得し、楽天用商品ページを自動生成
"""

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv
import logging

# 環境変数を読み込み
load_dotenv()

# Flaskアプリケーションを初期化
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ec-product-generator-key')

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmazonScraper:
    """Amazon商品情報取得クラス（基本バージョン）"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_product_info(self, asin):
        """ASINから商品情報を取得"""
        try:
            url = f"https://www.amazon.co.jp/dp/{asin}"
            logger.info(f"商品情報取得: {url}")
            
            # リクエスト
            time.sleep(random.uniform(1, 2))  # レート制限対策
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # HTML解析
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 商品情報を抽出
            product_data = {
                'asin': asin,
                'title': self._get_title(soup),
                'price': self._get_price(soup),
                'description': self._get_description(soup),
                'images': self._get_images(soup),
                'brand': self._get_brand(soup)
            }
            
            # データ検証
            if not product_data['title']:
                product_data['title'] = f"Amazon商品 (ASIN: {asin})"
            
            if not product_data['price']:
                product_data['price'] = "¥0"
            
            logger.info(f"商品情報取得完了: {product_data['title'][:50]}...")
            return product_data
            
        except Exception as e:
            logger.error(f"商品情報取得エラー: {str(e)}")
            return self._create_error_data(asin, str(e))
    
    def _get_title(self, soup):
        """商品タイトルを取得"""
        selectors = [
            '#productTitle',
            'span#productTitle',
            'h1.a-size-large',
            '[data-automation-id="title"]'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    if title and len(title) > 3:
                        return title
            except:
                continue
        
        return ""
    
    def _get_price(self, soup):
        """価格を取得"""
        selectors = [
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price .a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '.a-price-whole'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    price = element.get_text().strip()
                    if '¥' in price or price.replace(',', '').replace('.', '').isdigit():
                        return price if '¥' in price else f"¥{price}"
            except:
                continue
        
        return ""
    
    def _get_description(self, soup):
        """商品説明を取得"""
        descriptions = []
        
        # 特徴を取得
        try:
            feature_elements = soup.select('#feature-bullets ul li span.a-list-item')
            for element in feature_elements[:5]:
                text = element.get_text().strip()
                if text and len(text) > 10:
                    descriptions.append(text)
        except:
            pass
        
        # 商品説明を取得
        try:
            desc_element = soup.select_one('#productDescription p')
            if desc_element:
                desc_text = desc_element.get_text().strip()
                if desc_text and len(desc_text) > 20:
                    descriptions.append(desc_text)
        except:
            pass
        
        return '\n'.join(descriptions[:3]) if descriptions else "商品説明を取得中です。"
    
    def _get_images(self, soup):
        """商品画像を取得"""
        images = []
        
        try:
            # メイン画像
            main_img = soup.select_one('#landingImage')
            if main_img and main_img.get('src'):
                src = main_img.get('src')
                if 'amazon' in src:
                    images.append(src)
            
            # 追加画像
            img_elements = soup.select('.a-dynamic-image')
            for img in img_elements[:3]:
                src = img.get('src')
                if src and 'amazon' in src and src not in images:
                    images.append(src)
                    if len(images) >= 3:
                        break
        except:
            pass
        
        return images
    
    def _get_brand(self, soup):
        """ブランド名を取得"""
        try:
            brand_element = soup.select_one('#bylineInfo, a#bylineInfo')
            if brand_element:
                brand = brand_element.get_text().strip()
                brand = re.sub(r'^(ブランド:?|Brand:?)\s*', '', brand)
                return brand if len(brand) < 50 else ""
        except:
            pass
        
        return ""
    
    def _create_error_data(self, asin, error):
        """エラー時のデフォルトデータ"""
        return {
            'asin': asin,
            'title': f'商品情報取得エラー (ASIN: {asin})',
            'price': '¥0',
            'description': f'申し訳ございません。商品情報の取得に失敗しました。\nエラー: {error}\n\n手動で商品情報を入力してください。',
            'images': [],
            'brand': '',
            'error': error
        }

class RakutenGenerator:
    """楽天商品ページ生成クラス"""
    
    def __init__(self):
        self.profit_margin = 1.15  # 15%利益
    
    def generate_product(self, amazon_data):
        """楽天商品データを生成"""
        logger.info("楽天商品データ生成開始...")
        
        rakuten_data = {
            'item_name': self._optimize_title(amazon_data['title']),
            'item_price': self._calculate_price(amazon_data['price']),
            'item_description': self._generate_description(amazon_data),
            'catch_copy': self._generate_catch_copy(amazon_data),
            'item_url': self._generate_url(amazon_data['title']),
            'keywords': self._generate_keywords(amazon_data),
            'category_id': '100000',  # デフォルトカテゴリ
            'images': amazon_data['images'],
            'original_asin': amazon_data['asin']
        }
        
        logger.info("楽天商品データ生成完了")
        return rakuten_data
    
    def _optimize_title(self, title):
        """楽天用タイトル最適化"""
        if not title or "エラー" in title:
            return "【送料無料】高品質商品"
        
        # 文字数制限
        if len(title) > 120:
            title = title[:120] + "..."
        
        # キーワード追加
        if "送料無料" not in title and len(title) < 110:
            title = title + " 【送料無料】"
        
        return title
    
    def _calculate_price(self, amazon_price):
        """利益込み価格計算"""
        try:
            # 数字のみ抽出
            price_num = re.sub(r'[¥,円]', '', str(amazon_price))
            price_int = int(float(price_num))
            
            if price_int <= 0:
                return 1000
            
            # 利益率適用
            rakuten_price = int(price_int * self.profit_margin)
            
            # 切りの良い数字に調整
            if rakuten_price < 1000:
                rakuten_price = ((rakuten_price + 49) // 50) * 50
            else:
                rakuten_price = ((rakuten_price + 99) // 100) * 100
            
            return rakuten_price
            
        except:
            return 1000
    
    def _generate_description(self, amazon_data):
        """楽天用商品説明生成"""
        parts = []
        
        parts.append("■商品の特徴")
        if amazon_data.get('description'):
            parts.append(amazon_data['description'])
        else:
            parts.append("高品質な商品をお届けいたします。")
        
        if amazon_data.get('brand'):
            parts.append(f"\n■ブランド\n{amazon_data['brand']}")
        
        parts.append("\n■配送・サービス")
        parts.append("・全国送料無料")
        parts.append("・迅速発送")
        parts.append("・お気軽にお問い合わせください")
        
        return '\n'.join(parts)
    
    def _generate_catch_copy(self, amazon_data):
        """キャッチコピー生成"""
        brand = amazon_data.get('brand', '')
        if brand:
            return f"{brand}の人気商品！送料無料でお届け"
        return "人気商品！送料無料でお届け"
    
    def _generate_url(self, title):
        """商品URL生成"""
        url_safe = re.sub(r'[^a-zA-Z0-9]', '', str(title).lower())
        if len(url_safe) > 30:
            url_safe = url_safe[:30]
        
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{url_safe}_{timestamp}" if url_safe else f"product_{timestamp}"
    
    def _generate_keywords(self, amazon_data):
        """検索キーワード生成"""
        keywords = []
        
        # タイトルから抽出
        title = str(amazon_data.get('title', ''))
        words = title.split()[:5]
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 1:
                keywords.append(clean_word)
        
        # ブランド追加
        if amazon_data.get('brand'):
            keywords.append(amazon_data['brand'])
        
        # 定番キーワード追加
        keywords.extend(['送料無料', '高品質', '人気'])
        
        # 重複除去
        unique_keywords = list(dict.fromkeys(keywords))[:8]
        return ','.join(unique_keywords)

# Flaskルート
@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """ASIN→楽天商品データ生成API"""
    try:
        data = request.get_json()
        asin = data.get('asin', '').strip().upper()
        
        # バリデーション
        if not asin:
            return jsonify({'error': 'ASINを入力してください'}), 400
        
        if len(asin) != 10:
            return jsonify({'error': 'ASINは10文字で入力してください'}), 400
        
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            return jsonify({'error': 'ASINは英数字10文字で入力してください'}), 400
        
        logger.info(f"商品生成開始: ASIN={asin}")
        
        # Amazon商品情報取得
        scraper = AmazonScraper()
        amazon_data = scraper.get_product_info(asin)
        
        # 楽天商品データ生成
        generator = RakutenGenerator()
        rakuten_data = generator.generate_product(amazon_data)
        
        # レスポンス
        result = {
            'success': True,
            'amazon_data': amazon_data,
            'rakuten_data': rakuten_data,
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info("商品生成完了")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API エラー: {str(e)}")
        return jsonify({'error': f'処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/preview/<asin>')
def preview(asin):
    """商品プレビュー"""
    try:
        scraper = AmazonScraper()
        amazon_data = scraper.get_product_info(asin)
        
        generator = RakutenGenerator()
        rakuten_data = generator.generate_product(amazon_data)
        
        return render_template('preview.html', 
                             amazon_data=amazon_data, 
                             rakuten_data=rakuten_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    print("EC商品ページ自動作成システム起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    app.run(debug=True, host='127.0.0.1', port=5000)
