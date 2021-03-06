html_style = """
    <style>
        body {
            font-family: "Noto Sans", sans-serif;
            font-size: 8px;
            line-height: 1.25;
        }

        .title {
            font-weight: bold;
            font-size: 14px;
            text-align: center;
        }

        .subtitle {
            font-style: italic;
            text-align: center;
            margin-bottom: 20px;
            color: gray;
        }

        .newspaper-name {
            text-align: center;
            font-weight: bold;
            font-size: 12px;
        }

        .newspaper-info {
            margin-bottom: 10px;
            text-align: center;
            font-style: italic;
            font-size: 6px;
            color: gray;
        }

        .news-list {
            columns: 2;
            column-gap: 20px;
            column-fill: balance;
            margin-bottom: 20px;
        }

        .news-box {
            display: flex;
            flex-direction: column;
            margin-bottom: 5px;
            border-bottom: 1px solid black;
        }

        .news-content {
            display: flex;
        }

        .news-text {
            flex: 1;
            text-align: justify;
        }

        .news-title {
            font-weight: bold;
        }

        .news-qrcode {
            margin-left: 10px;
        }

        .news-info {
            display: flex;
            justify-content: space-between;
            margin: 1px 0;
            font-style: italic;
            font-size: 6px;
            color: gray;
        }          
    </style>
"""

pdf_style = """
    @page {
        size: A4;
        margin: 10mm;
    }
"""
