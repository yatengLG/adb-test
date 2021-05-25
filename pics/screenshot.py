# -*- coding: utf-8 -*-
# @Author  : LG

from device_ops.device_ops import ScreenCap
import cv2

path = ScreenCap(device_id='jjypof7xcqzpg6pn')
img = cv2.imread(path)

img=img[405:765, 1510:1990]

cv2.imwrite('1510-405-1990-765.png', img)