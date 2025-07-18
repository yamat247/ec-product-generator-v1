# EC Product Page Generator

This project provides a simple Flask web application that creates a product description page for Rakuten based on an Amazon ASIN. The tool scrapes information from Amazon, generates Rakuten-friendly content, and lets you preview the result.

## Installation

1. Clone this repository and navigate into the project directory.
2. Install the required Python packages:

```bash
pip install flask requests beautifulsoup4 python-dotenv
```

## Usage

1. Prepare a `.env` file in the project root with the following variable:

```
SECRET_KEY=your-secret-key
```

2. Start the Flask server:

```bash
python app.py
```

The application will launch at `http://localhost:5000/`. Enter an ASIN on the page, and the app will fetch product data from Amazon and generate a sample Rakuten page for preview.

## What It Does

- Retrieves Amazon product information using the provided ASIN.
- Converts that information into a format suitable for listing on Rakuten.
- Lets you preview the generated page directly in your browser.

This tool is intended to streamline creating product listings when transferring goods from Amazon to Rakuten.
