import glob
import os 
import json

from download import Downloader

for ticker_file in glob.glob("stock-data/*.json"):
    if ticker_file.endswith("10q.json"):
        continue

    ticker = os.path.basename(ticker_file.replace(".json", ""))

    res = glob.glob(f"data/{ticker}/**/*.htm")
    if len(res) > 0:
        continue

    print(ticker.upper())
    
    downloader = Downloader(ticker.upper())

    try:
        downloader.download(last=10, only_html=True)
    except Exception as e:
        print(f"ERR: {str(e)}")