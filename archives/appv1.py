# coding=UTF-8
from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import uuid
import os

app = Flask(__name__)

def show(name):
  cv2.imshow('Show', name)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

@app.route("/", methods=['POST', 'GET'])
def analyse():
  try:
    # 拿到body数据
    postData = request.json
    # 缺口图转为mat格式
    target_img_data  = base64.b64decode(postData['target'])
    target_img_array = np.fromstring(target_img_data, np.uint8)
    target = cv2.imdecode(target_img_array, cv2.IMREAD_GRAYSCALE)
    # 底图转为mat格式
    template_img_data  = base64.b64decode(postData['template'])
    template_img_array = np.fromstring(template_img_data, np.uint8)
    template = cv2.imdecode(template_img_array, cv2.IMREAD_GRAYSCALE)

    w, h = target.shape
    # 生成临时文件
    id = str(uuid.uuid1())
    temp_template = 'temp_template'+id+'.jpg'
    temp_target = 'temp_target'+id+'.jpg'
    cv2.imwrite(temp_template, template)
    cv2.imwrite(temp_target, target)
    target = cv2.imread(temp_target)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target = abs(255 - target)
    cv2.imwrite(temp_target, target)
    target = cv2.imread(temp_target)
    template = cv2.imread(temp_template)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    show(template)
    print( x, y,y + w, x + h)
    os.remove(temp_template)  
    os.remove(temp_target)  
  except TypeError:
    return jsonify(error='image format analyse failed')
  else:
    return jsonify(
      x1 = str(y),
      y1 = str(x),
      x2 = str(y + w),
      y2 = str(x + h),
    )

app.run(host='127.0.0.1', port=5000)