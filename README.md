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
