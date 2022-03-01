import requests
import os 
import threading, queue
import mysql.connector
import time
import datetime

api_key = os.environ['FMP_API_KEY']
q = queue.Queue()

now = datetime.datetime.now()
tya = now - datetime.timedelta(days=20*365)

def worker():
    db = mysql.connector.connect(
        host='192.168.1.125',
        user='root',
        password=os.environ['MYSQL_PASS'],
        port='30497',
        database='expensifier'
    )

    while True:
        ticker = q.get()
        if ticker is None:
            break
        
        cursor = db.cursor()
        print(f"Processing {ticker}")
        
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={api_key}"
        res = requests.get(url)
        data = res.json()
        
        for item in data['historical']:
            if datetime.datetime.fromisoformat(item['date']) < tya:
                continue
            
            query = "INSERT IGNORE INTO prices (ticker, date, price) VALUES (%s, %s, %s)"
            cursor.execute(query, (ticker, item['date'], item['close']))
        
        db.commit()
        cursor.close()
        time.sleep(1)
        q.task_done()

    db.close()

for i in range(10):
    threading.Thread(target=worker).start()
    
r = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}")
for entry in r.json():
    print(f"Adding {entry['symbol']} to queue")
    q.put(entry['symbol'])

q.join()
print('All work completed')