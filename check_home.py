import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

resp = requests.get('https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/page/ppr-home-en', verify=False)
soup = BeautifulSoup(resp.text, 'html.parser')

links = soup.find_all('a')
for l in links:
    if 'download' in l.text.lower() or 'csv' in l.text.lower():
        print(f"Link: text={repr(l.text.strip())}, class={l.get('class')}, href={l.get('href')}")
