# coding=UTF-8
from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import uuid
import os
import pytesseract
from PIL import Image

app = Flask(__name__)


def show(name):
  cv2.imshow('Show', name)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def remove_blank(list):
  result = []
  for s in list:
    result.append(s.replace(' ', ''))
  return result

def _tran_canny(image):
  """消除噪声"""
  image = cv2.GaussianBlur(image, (3, 3), 0)
  return cv2.Canny(image, 50, 150)


def writeFile(b64):
  # 图片转为mat格式
  target_img_data  = base64.b64decode(b64)
  target_img_array = np.frombuffer(target_img_data, np.uint8)
  target = cv2.imdecode(target_img_array, cv2.IMREAD_GRAYSCALE)

  w, h = target.shape
  # 生成临时文件
  id = str(uuid.uuid1())
  temp_target = 'temp_target_'+id+'.jpg' 
  cv2.imwrite(temp_target, target)
  return temp_target,target


def ocr(b64Data):
  #  参数0是灰度模式
  image = cv2.imread(b64Data, 0)
  # show(image)
  # 将图片做二值化处理，阈值设定为127，将像素值大于127的置为0，小于127的置为255
  ret, im_inv = cv2.threshold(image,127,255,cv2.THRESH_BINARY_INV)
  # show(im_inv)

  # 构建卷积核的数据集，实现模糊成像的效果
  kernel = 1/16*np.array([[1,2,1], [2,4,2], [1,2,1]])
  # 使用高斯模糊对图片进行降噪
  im_blur = cv2.filter2D(im_inv,-1,kernel)
  # show(im_blur)

  # 将图片做二值化处理，阈值设定为185，将像素值大于127的置为0，小于127的置为255
  ret, im_res = cv2.threshold(im_blur,150,255,cv2.THRESH_BINARY)
  # show(im_res)

  # 改为白色底色，黑色字
  cv2.bitwise_not(im_res, im_res)
  # show(im_res)
  return im_res


def tesseract(im_res,lang):
  test_message = Image.fromarray(im_res)
  tessdata_dir = "--psm 7 --tessdata-dir "+os.path.abspath("/tessdata")
  text = pytesseract.image_to_string(test_message,config=tessdata_dir,lang=lang)
  # print(f'识别结果：{text}')
  return text.replace("\n", "").replace("\f","")


@app.route("/ping", methods=['POST', 'GET'])
def pong():
  return 'pong'


@app.route("/ocr/base64", methods=['POST', 'GET'])
def analyzeOcr():
  postData = request.json
  result = []
  type = request.args.get("type")
  accept_type = ["pkjy.num","pkjy.alphabet_num"]
  if type not in accept_type:
    type = "pkjy.alphabet_num"
  for b64 in postData['base64']:
    try:
      filePath = writeFile(b64)[0]
      result.append(tesseract(ocr(filePath),type))
    except Exception as e:
      os.remove(filePath)  
      print(e)
      return jsonify(error='analyze failed')
    else:
      os.remove(filePath)  
  print("result",remove_blank(result))
  return jsonify(code = 0,result = remove_blank(result))


@app.route("/slide/base64", methods=['POST', 'GET'])
def analyzeSlide():
  try:
    # https://cloud.tencent.com/developer/article/1825224
    # 拿到query参数
    useCanny = request.args.get('canny')
    # 拿到body数据
    postData = request.json

    # b64转本地文件
    temp_target,target = writeFile(postData['target'])
    temp_template = writeFile(postData['template'])[0]
    w, h = target.shape

    # """detect displacement"""
    # # 参数0是灰度模式
    image = cv2.imread(temp_target, 0)
    template = cv2.imread(temp_template, 0)
    
    # 寻找最佳匹配
    if useCanny:
      res = cv2.matchTemplate(_tran_canny(image), _tran_canny(template), cv2.TM_CCOEFF_NORMED)
    else:
      res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    # 最小值，最大值，并得到最小值, 最大值的索引
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc[0]  # 横坐标
    # 展示圈出来的区域
    x, y = max_loc  # 获取x,y位置坐标

    w, h = image.shape[::-1]  # 宽高
    cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
    os.remove(temp_template)  
    os.remove(temp_target)  
    # show(template)

  except TypeError:
    return jsonify(error='image format analyze failed')
  else:
    return jsonify(code=0,result={
      "x1" : str(x),
      "y1" : str(y),
      "x2" : str(x + h),
      "y2" : str(y + w),
    }
    )

app.run(host='0.0.0.0', port=5000)