import mysql.connector 
import os 
import datetime
import sys
import requests
import matplotlib.pyplot as plt 
import numpy as np

class Plotter:
    def __init__(self, debug=False):
        self.api_key = os.environ['FMP_API_KEY']
        if not self.api_key:
            raise ValueError("FMP_API_KEY not set")

        self.db = mysql.connector.connect(
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASS'],
            port=os.environ['MYSQL_PORT'],
            database='expensifier'
        )
        self.cursor = self.db.cursor()
        self.sp500_prices = self.get_sp500_prices()
        self.debug = debug

        self.x_array = []
        self.y_array = []

    # def __del__(self):
    #     self.cursor.close()
    #     self.db.close()

    def get_sp500_prices(self):
        sp500_prices = {}
        res = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/VOO?serietype=line&apikey={self.api_key}")
        for day in res.json()['historical']:
            sp500_prices[day['date']] = day['close']
        return sp500_prices

    def comp(self, a, b):
        if b == 0:
            return 0
        return round(100*(1-(float(a)/float(b))), 2)

    def plot(self):
        r = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={self.api_key}")
        for entry in r.json():
            self.plot_ticker(entry['symbol'])

    def generate_graph(self):
        fig, ax = plt.subplots()
        ax.set_ylabel('Real earnings vs reported net income')
        ax.set_xlabel('Price performance over 12 months')
        x = np.array(self.x_array)
        y = np.array(self.y_array)
        ax.scatter(x, y)
        plt.show()

    def plot_ticker(self, ticker):
        days = {}
        prices = self.cursor.execute("SELECT date, price FROM prices WHERE ticker = %s", (ticker,))
        for row in self.cursor.fetchall():
            days[row[0]] = row[1]

        excluded_cols = ['expenses_depreciation_amortization', 'expenses_interest']

        expenses = {}
        filings = self.cursor.execute("SELECT * FROM filings WHERE ticker = %s", (ticker,))
        col_names = [i[0] for i in self.cursor.description]
        for row in self.cursor.fetchall():
            total_expenses = 0
            for k, v in enumerate(row):
                col_name = col_names[k]
                if col_name.startswith("expenses_") and col_name not in excluded_cols:
                    total_expenses += v
            if row[3] == '10-K':
                continue
            expenses[row[2]] = {"expenses": int(total_expenses), "netIncome": 0}

        statements = self.cursor.execute("SELECT fillingDate, netIncome FROM fundamentals WHERE ticker = %s", (ticker,))
        for row in self.cursor.fetchall():
            date = row[0]
            if date in expenses:
                expenses[date]['netIncome'] = row[1]

        for date, expense in expenses.items():
            adjusted_ni = expense['netIncome'] - expense['expenses']
            comparison = self.comp(expense['netIncome'], adjusted_ni)

            next_year_date = datetime.date(date.year+1, date.month, date.day)
            if next_year_date in days and date in days:
                curr_price = days[date]
                next_price = days[next_year_date]

                sp_curr = self.sp500_prices[date.strftime("%Y-%m-%d")]
                sp_next = self.sp500_prices[next_year_date.strftime("%Y-%m-%d")]

                price_comparison = self.comp(curr_price, next_price) - self.comp(sp_curr, sp_next)
                # price_comparison = self.comp(curr_price, next_price)

                self.x_array.append(comparison)
                self.y_array.append(price_comparison)
                
            if self.debug:
                print(f"Net income {expense['netIncome']/1000000}")
                print(f"Actual income {adjusted_ni/1000000} ({comparison}%)")
                print(f"{date} price = {curr_price}")
                print(f"{next_year_date} price = {next_price}")
                print(f"Increase = {self.comp(curr_price, next_price)} S&P = {self.comp(sp_curr, sp_next)}")

                print(comparison)
                print(price_comparison)
                print("\n")


if __name__ == '__main__':
    ticker = sys.argv[1]
    p = Plotter()
    p.plot()
    p.generate_graph()