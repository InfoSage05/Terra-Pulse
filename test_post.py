import requests
import urllib3

urllib3.disable_warnings()

session = requests.Session()

# 1. Fetch form first to get cookies/session initialized if needed
form_url = 'https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPRDownloads?OpenForm'
print("GET", form_url)
resp = session.get(form_url, verify=False)
print("GET Status:", resp.status_code)
print("GET Cookies:", session.cookies.get_dict())

# 2. Prepare POST parameters
post_url = 'https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/PPRDownloads?OpenForm&Seq=1'
data = {
    '__Click': '0',
    'browser': 'xx99',
    'webServerName': 'https://www.propertypriceregister.ie',
    'webDBName': '/website/npsra/pprweb.nsf',
    'urlLang': 'en',
    '%%Surrogate_County': '1',
    'County': 'Dublin',
    '%%Surrogate_Year': '1',
    'Year': '2024',
    '%%Surrogate_Month': '1',
    'Month': 'ALL'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': form_url,
    'Origin': 'https://www.propertypriceregister.ie'
}

print("POST", post_url)
resp_post = session.post(post_url, data=data, headers=headers, verify=False)
print("POST Status:", resp_post.status_code)
print("POST Content-Type:", resp_post.headers.get('content-type'))
print("POST Cookies:", session.cookies.get_dict())

# Save output to see what it is
with open('post_response.html', 'wb') as f:
    f.write(resp_post.content)
print("Saved post_response.html")

# Let's inspect if it's CSV or HTML. If HTML, look for CSV download links
content_preview = resp_post.text[:1000]
print("Content Preview:\n", content_preview)
