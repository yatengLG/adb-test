# -*- coding: utf-8 -*-
# @Author  : LG

import cv2
import numpy as np

def pHash(img):
    # 感知哈希算法
    # 缩放32*32
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC

    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash


def cmpHash(hash1, hash2):
    # Hash值对比
    # 算法中1和0顺序组合起来的即是图片的指纹hash。顺序不固定，但是比较的时候必须是相同的顺序。
    # 对比两幅图的指纹，计算汉明距离，即两个64位的hash值有多少是不一样的，不同的位数越小，图片越相似
    # 汉明距离：一组二进制数据变成另一组数据所需要的步骤，可以衡量两图的差异，汉明距离越小，则相似度越高。汉明距离为0，即两张图片完全一样
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n


def calculate(img1, img2):
    hash1 = pHash(img1)
    hash2 = pHash(img2)
    n = cmpHash(hash1, hash2)
    return (64-n)/64

if __name__ == '__main__':
    img = cv2.imread('/home/super/PycharmProjects/untitled1/pics/farm_level_685-405-1165-765.png')
    img1 = cv2.imread('/home/super/PycharmProjects/untitled1/pics/gold_level_1510-405-1990-765.png')
    img2 = cv2.imread('/home/super/PycharmProjects/untitled1/pics/stone_level_1235-405-1715-765.png')

    r1 = calculate(img, img1)
    r2 = calculate(img, img2)
    print(r1, r2)
