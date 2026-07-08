import requests
import urllib3
urllib3.disable_warnings()

url = 'https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/$FILE/PPR-ALL.zip'
print('Downloading...', url)
resp = requests.get(url, verify=False, allow_redirects=True, stream=True)
print('Status:', resp.status_code)
print('Content-Type:', resp.headers.get('content-type'))
content_len = resp.headers.get('content-length')
print('Length:', content_len)

if resp.status_code == 200:
    if 'html' not in resp.headers.get('content-type', '').lower():
        with open('PPR-ALL.zip', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192): 
                f.write(chunk)
        print('Saved PPR-ALL.zip')
    else:
        print('Got HTML instead of zip! Probably bot challenge.')
