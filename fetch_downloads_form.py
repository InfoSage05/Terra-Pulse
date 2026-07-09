import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

url = 'https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPRDownloads?OpenForm'
print("Fetching:", url)
resp = requests.get(url, verify=False)
html = resp.text

with open('ppr_downloads_form.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved ppr_downloads_form.html")

soup = BeautifulSoup(html, 'html.parser')
for form in soup.find_all('form'):
    print(f"Form name={form.get('name')}, action={form.get('action')}, method={form.get('method')}")
    for inp in form.find_all('input'):
        print(f"  Input: name={inp.get('name')}, type={inp.get('type')}, value={repr(inp.get('value'))}")
    for sel in form.find_all('select'):
        print(f"  Select: name={sel.get('name')}")
        for opt in sel.find_all('option')[:5]:
            print(f"    Option: value={repr(opt.get('value'))}, text={repr(opt.text.strip())}")
