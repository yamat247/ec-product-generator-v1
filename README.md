# EC Product Generator

This Flask application retrieves product details from Amazon using an ASIN and generates
page data suitable for listing on Rakuten.

## Running the application

Install dependencies first:

```bash
pip install flask requests beautifulsoup4 python-dotenv
```

Start the server:

```bash
python app.py
```

By default the service runs on `http://localhost:5000`.

## Testing the Rakuten API

An endpoint `/api/test-rakuten` sends a POST request to the Rakuten
`sample.order` API and logs the response. Trigger the test with curl:

```bash
curl http://localhost:5000/api/test-rakuten
```

The status code and body returned by Rakuten will be shown in the
command output and logged by the application.
=======
# EC Product Page Generator

This project provides a simple Flask web application that creates a product description page for Rakuten based on an Amazon ASIN. The tool scrapes information from Amazon, generates Rakuten-friendly content, and lets you preview the result.

## Installation（セットアップ）

1. Python 3 をインストールします。
2. 次のコマンドで必要なパッケージをインストールします：

```bash
pip install -r requirements.txt