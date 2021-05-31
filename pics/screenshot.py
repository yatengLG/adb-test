# -*- coding: utf-8 -*-
# @Author  : LG

from device_ops.device_ops import ScreenCap
import cv2

path = ScreenCap(device_id='jjypof7xcqzpg6pn')
img = cv2.imread(path)

img=img[440:620, 1400:1710]

#   1945 170 250

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imwrite('验证_1400-440-1710-620.png', img)

# import os
#
# files = os.listdir(os.getcwd())
# print(files)
#
# pngs = [f for f in files if f.endswith('.png')]
#
# for png in pngs:
#     img = cv2.imread(png)
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     cv2.imwrite(png, img)


