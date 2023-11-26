import requests

res = requests.get("http://185.254.206.129/get_json_dataset", params={'api_key': '948373984739874'})
print(res.json())