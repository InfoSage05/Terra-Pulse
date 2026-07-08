from bs4 import BeautifulSoup
import sys

with open('ppr_results.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print('--- IMAGES ---')
for img in soup.find_all('img'):
    print(f"img: src={img.get('src')}, alt={img.get('alt')}, title={img.get('title')}")

print('--- BUTTONS ---')
for btn in soup.find_all('button'):
    print(f"button: text={repr(btn.text.strip())}, class={btn.get('class')}")

print('--- ANY ELEMENT WITH ONCLICK OR HREF CONTAINING CSV ---')
for el in soup.find_all():
    onclick = el.get('onclick')
    href = el.get('href')
    if onclick and 'csv' in onclick.lower():
        print(f"{el.name} onclick: {onclick}")
    if href and 'csv' in href.lower():
        print(f"{el.name} href: {href}")
        
print('--- ANY ELEMENT CONTAINING TEXT CSV OR DOWNLOAD ---')
for el in soup.find_all(string=lambda text: text and ('csv' in text.lower() or 'download' in text.lower())):
    if el.parent:
        print(f"Text node parent {el.parent.name}: {repr(el)}")
