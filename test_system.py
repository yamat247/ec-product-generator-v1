# EC商品ページ自動作成システム - テストスクリプト

import requests
import json
from app import AmazonScraper, RakutenGenerator

def test_system():
    """システムの基本動作をテスト"""
    
    # テスト用ASIN（適当な例）
    test_asin = "B08N5WRWNW"  # Echoの例
    
    print(f"=== システムテスト開始 ===")
    print(f"テストASIN: {test_asin}")
    
    try:
        # Amazon商品情報取得テスト
        print("\n1. Amazon商品情報取得テスト...")
        scraper = AmazonScraper()
        amazon_data = scraper.get_product_info(test_asin)
        
        print(f"商品名: {amazon_data['title'][:50]}...")
        print(f"価格: {amazon_data['price']}")
        print(f"説明: {amazon_data['description'][:100]}...")
        print(f"画像数: {len(amazon_data['images'])}")
        print(f"ブランド: {amazon_data['brand']}")
        
        # 楽天商品データ生成テスト
        print("\n2. 楽天商品データ生成テスト...")
        generator = RakutenGenerator()
        rakuten_data = generator.generate_product(amazon_data)
        
        print(f"楽天商品名: {rakuten_data['item_name'][:50]}...")
        print(f"楽天価格: ¥{rakuten_data['item_price']:,}")
        print(f"キャッチコピー: {rakuten_data['catch_copy']}")
        print(f"商品URL: {rakuten_data['item_url']}")
        print(f"キーワード: {rakuten_data['keywords']}")
        
        print("\n=== テスト完了: 正常動作確認 ===")
        return True
        
    except Exception as e:
        print(f"\n=== テスト失敗: {str(e)} ===")
        return False

if __name__ == "__main__":
    test_system()
