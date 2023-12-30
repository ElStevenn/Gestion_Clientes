import schedule
import time
import requests

"""

Script to make api requests every 10 secods, is used to 
update an internal dataset.

Service name -> internalfeat.service

Start this script -> sudo systemctl start internalfeat.service
Restart this script -> sudo systemctl restart internalfeat.service
Stop this script -> sudo systemctl stop internalfeat.service
See status -> sudo systemctl status internalfeat.service

"""

url1 = "http://inutil.top/update_dataset"
header = {
   'Content-Type': 'application/json',
  'api-key':"rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8="
}

def read_data_call():
    try:
        requests.patch(url1, headers=header)
        time.sleep(0.2)
        response = requests.patch(url1, headers=header)
        print(f"Response: {response.status_code}, {response.text}")
    except:
        print("The server is currently turned off")

schedule.every(2).seconds.do(read_data_call)
while True:
    schedule.run_pending()
    time.sleep(1)

