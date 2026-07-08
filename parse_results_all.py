from bs4 import BeautifulSoup

with open('ppr_results.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

links = soup.find_all('a')
print(f"Total links on results page: {len(links)}")
for l in links:
    print(f"Link: text={repr(l.text.strip())}, class={l.get('class')}")
        
inputs = soup.find_all('input')
for i in inputs:
    print(f"Input: value={repr(i.get('value'))}, type={i.get('type')}, class={i.get('class')}")
