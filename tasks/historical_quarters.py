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
        host=os.environ['MYSQL_HOST'],
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASS'],
        port=os.environ['MYSQL_PORT'],
        database='expensifier'
    )

    while True:
        ticker = q.get()
        if ticker is None:
            break
        
        cursor = db.cursor()
        print(f"Processing {ticker}")
        
        url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=400&apikey={api_key}"
        res = requests.get(url)
        data = res.json()
        
        for d in data:
            if datetime.datetime.fromisoformat(d['date']) < tya:
                continue
            
            query = """
            INSERT IGNORE INTO fundamentals (
                ticker, filing_date, reportedCurrency, fillingDate, acceptedDate, calendarYear, period, 
                revenue, costOfRevenue, grossProfit, grossProfitRatio, researchAndDevelopmentExpenses, 
                generalAndAdministrativeExpenses, sellingAndMarketingExpenses, 
                sellingGeneralAndAdministrativeExpenses, otherExpenses, operatingExpenses, costAndExpenses, 
                interestIncome, interestExpense, depreciationAndAmortization, ebitda, ebitdaratio, 
                operatingIncome, operatingIncomeRatio, totalOtherIncomeExpensesNet, incomeBeforeTax, 
                incomeBeforeTaxRatio, incomeTaxExpense, netIncome, netIncomeRatio, eps, epsdiluted, 
                weightedAverageShsOut, weightedAverageShsOutDil
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                ticker=VALUES(ticker), filing_date=VALUES(filing_date), reportedCurrency=VALUES(reportedCurrency), fillingDate=VALUES(fillingDate), acceptedDate=VALUES(acceptedDate), calendarYear=VALUES(calendarYear), period=VALUES(period), 
                revenue=VALUES(revenue), costOfRevenue=VALUES(costOfRevenue), grossProfit=VALUES(grossProfit), grossProfitRatio=VALUES(grossProfitRatio), researchAndDevelopmentExpenses=VALUES(researchAndDevelopmentExpenses), 
                generalAndAdministrativeExpenses=VALUES(generalAndAdministrativeExpenses), sellingAndMarketingExpenses=VALUES(sellingAndMarketingExpenses), 
                sellingGeneralAndAdministrativeExpenses=VALUES(sellingGeneralAndAdministrativeExpenses), otherExpenses=VALUES(otherExpenses), operatingExpenses=VALUES(operatingExpenses), costAndExpenses=VALUES(costAndExpenses), 
                interestIncome=VALUES(interestIncome), interestExpense=VALUES(interestExpense), depreciationAndAmortization=VALUES(depreciationAndAmortization), ebitda=VALUES(ebitda), ebitdaratio=VALUES(ebitdaratio), 
                operatingIncome=VALUES(operatingIncome), operatingIncomeRatio=VALUES(operatingIncomeRatio), totalOtherIncomeExpensesNet=VALUES(totalOtherIncomeExpensesNet), incomeBeforeTax=VALUES(incomeBeforeTax), 
                incomeBeforeTaxRatio=VALUES(incomeBeforeTaxRatio), incomeTaxExpense=VALUES(incomeTaxExpense), netIncome=VALUES(netIncome), netIncomeRatio=VALUES(netIncomeRatio), eps=VALUES(eps), epsdiluted=VALUES(epsdiluted), 
                weightedAverageShsOut=VALUES(weightedAverageShsOut), weightedAverageShsOutDil=VALUES(weightedAverageShsOutDil)
            """
            values = (d['symbol'], d['date'], d['reportedCurrency'], d['fillingDate'], d['acceptedDate'], d['calendarYear'], d['period'], 
                d['revenue'], d['costOfRevenue'], d['grossProfit'], d['grossProfitRatio'], d['researchAndDevelopmentExpenses'], 
                d['generalAndAdministrativeExpenses'], d['sellingAndMarketingExpenses'], 
                d['sellingGeneralAndAdministrativeExpenses'], d['otherExpenses'], d['operatingExpenses'], d['costAndExpenses'], 
                d['interestIncome'], d['interestExpense'], d['depreciationAndAmortization'], d['ebitda'], d['ebitdaratio'], 
                d['operatingIncome'], d['operatingIncomeRatio'], d['totalOtherIncomeExpensesNet'], d['incomeBeforeTax'], 
                d['incomeBeforeTaxRatio'], d['incomeTaxExpense'], d['netIncome'], d['netIncomeRatio'], d['eps'], d['epsdiluted'], 
                d['weightedAverageShsOut'], d['weightedAverageShsOutDil'])
            cursor.execute(query, values)
        
        db.commit()
        cursor.close()
        time.sleep(1)
        q.task_done()

    db.close()

for i in range(1):
    threading.Thread(target=worker).start()
    
r = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}")
for entry in r.json():
    print(f"Adding {entry['symbol']} to queue")
    q.put(entry['symbol'])

q.join()
print('All work completed')