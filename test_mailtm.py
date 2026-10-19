import requests
res = requests.get("https://box.celana-ar-store.my.id/domains", verify=False)
print(res.status_code, res.text)
