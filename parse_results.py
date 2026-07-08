from bs4 import BeautifulSoup
import sys

with open('ppr_results.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

links = soup.find_all('a')
for l in links:
    if 'download' in l.text.lower() or 'csv' in l.text.lower() or 'results' in l.text.lower():
        print(f"Link: text={repr(l.text.strip())}, class={l.get('class')}")
        
inputs = soup.find_all('input')
for i in inputs:
    if i.get('type') in ['submit', 'button'] and ('download' in str(i.get('value')).lower() or 'csv' in str(i.get('value')).lower()):
        print(f"Input: value={repr(i.get('value'))}, name={i.get('name')}")
