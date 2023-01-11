import requests
import os
import json
import base64
url = "http://127.0.0.1:5000/ocr/base64"


headers = {
  'Content-Type': 'application/json',
  'Cookie': 'locale=en-us'
}


success = 0
total = 0

def check(file_name,base64_data):
  global success
  payload = json.dumps({
    "base64": [
      str(base64_data, 'utf-8') 
    ]
  })
  response = requests.request("GET", url, headers=headers, data=payload)
  if json.loads(response.text).get('result')[0]==file_name.split('_')[0] :
    print(file_name.split('_')[0],'相等')
    success += 1
  else:
    print(file_name.split('_')[0],'不相等')

if __name__ == '__main__':
  g = os.walk(r"./examples/ocr")
  for path,dir_list,file_list in g:
    for file_name in file_list:
      with open(os.path.join(path, file_name), 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data)  # base64编码
        (file,ext) = os.path.splitext(file_name)
        total += 1
        check(file,base64_data)
        # print(type(base64_data))
  print('成功率:',round(success/total*100,2),'%')
