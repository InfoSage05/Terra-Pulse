from bs4 import BeautifulSoup
import sys

with open('ppr_form.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

links = soup.find_all('a')
print(f"Total links: {len(links)}")
for l in links:
    if 'search' in l.text.lower() or 'search' in str(l.get('class')):
        print(f"Link: text={repr(l.text.strip())}, class={l.get('class')}")
        
inputs = soup.find_all('input')
for i in inputs:
    if i.get('type') in ['submit', 'button'] and ('search' in str(i.get('value')).lower() or 'search' in str(i.get('name')).lower()):
        print(f"Input: value={repr(i.get('value'))}, name={i.get('name')}")
