import mysql.connector
import requests
import sys
from faker import Faker
import os


class Filing:
    def __init__(self, filing_type, date, accnum):
        self.type = filing_type 
        self.date = date 
        self.accnum = accnum

class UrlRetriever:
    def __init__(self, cik):
        self.cik = cik

    def user_agent(self):
        fake = Faker()
        return f"{fake.first_name()} {fake.last_name()} {fake.email()}"

    def cik_json(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        req = requests.get(url, headers={"User-Agent": self.user_agent()})
        return req.json()
    
    def get_all_years(self):
        db = mysql.connector.connect(
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASS'],
            database='expensifier'
        )

        data = self.cik_json()
        data = data['filings']['recent']

        items = []
        for key, val in enumerate(data['form']):
            if val in ['10-K', '10-Q']:
                f = Filing(val, data['filingDate'][key], data['accessionNumber'][key])
                items.append(f)

        for item in items:
            query = "INSERT INTO filing_meta (cik, filing_type, filing_date, accession_number) VALUES (%s, %s, %s, %s)"
            values = (self.cik, item.type, item.date, item.accnum)
            db.cursor().execute(query, values)
            db.commit()

if __name__ == "__main__":
    ur = UrlRetriever(sys.argv[1], False)
    ur.get_all_years()