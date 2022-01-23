from typing import List
from collections import namedtuple
import time 
import random
import string
from pathlib import Path
import os

import requests

def same_month_year(a, b):
    return a.year == b.year and a.month == b.month

def fetch_url(url, filing_dir):
    path = f"{filing_dir}/{os.path.basename(url)}"
    r = requests.get(url, stream=True, headers={"User-Agent": random_str()})
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        print(f"{r.status_code} err: {url}")
    return r

def strip_xml_ns(name, lower=True):
    if ":" in name:
        name = name.split(":")[1]
    if lower:
        name = name.lower()
    return name