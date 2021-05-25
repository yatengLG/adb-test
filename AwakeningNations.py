# -*- coding: utf-8 -*-
# @Author  : LG

import subprocess
from cv_ops import similar
from device_ops import device_ops, device_info
import cv2
import random
import time
import logging


class Miner():
    def __init__(self, device_id):
        self.logger = logging.getLogger()
        self.logger.setLevel(level=logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler("logs/{}.txt".format(device_id))  # 文件处理器
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)

        console = logging.StreamHandler()  # 控制台处理器
        console.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)  # 添加文件输出
        self.logger.addHandler(console)  # 添加控制台输出

        self.device_id = device_id
        self.app = "com.lilithgames.rok.offical.cn/com.harry.engine.MainActivity"

        self.home_button = (155, 945, 40)    # c 155 945, xmin ,xmax, ymin, ymax
        self.search_button = (150, 780, 20) # c 150 780

        #                        cx   cy   w/2 bias
        self.barbarian_button = (650, 910, 50, 15) # 野蛮人   470 865
        self.farm_button = (925, 910, 50, -5)   # 田         725 1120
        self.wood_button = (1200, 910, 50, 0)  # 木         1005 1400
        self.stone_button = (1475, 910, 50, 0) # 石         1280 1675
        self.gold_button = (1750, 910, 50, 0)  # 金         1555 1950

    def open_app(self):
        try:
            sub = subprocess.Popen('adb -s {} shell am start -n {}'.format(self.device_id, self.app), shell=True)
            sub.wait(10)
            if sub.returncode == 0:
                self.logger.info("打开app")
                time.sleep(10)
                return True
            else:
                return -1
        except:
            return -1


    def in_city(self):
        screen_pic = device_ops.ScreenCap(self.device_id)
        home_pic = cv2.imread(screen_pic)[
                     self.home_button[1] - self.home_button[2]:self.home_button[1] + self.home_button[2],
                     self.home_button[0] - self.home_button[2]:self.home_button[0] + self.home_button[2],
                     ]    # (155, 945, 45)
        home_map_img = cv2.imread('/home/super/PycharmProjects/untitled/pics/home_map.png')
        home_city_img = cv2.imread('/home/super/PycharmProjects/untitled/pics/home_city.png')
        home_hash = similar.pHash(home_pic)
        map_hash = similar.pHash(home_map_img)
        city_hash = similar.pHash(home_city_img)
        n_map = similar.cmpHash(home_hash, map_hash)
        n_city = similar.cmpHash(home_hash, city_hash)
        self.logger.info("判断是否在城内, n_map:{} | n_city:{}".format(n_map, n_city))
        if n_map > n_city:  # 当前图标为city图标，在野外，可挖矿
            return False
        else:
            return True

    def cal_similar(self, image:str, area=None):
        """

        :param image:
        :param area:    xmin ymin xmax ymax
        :return:
        """
        if area is None:
            area = [int(n) for n in image.rstrip('.png').split('_')[-1].split('-')]
        screen = device_ops.ScreenCap(self.device_id)
        screen = cv2.imread(screen)[area[1]:area[3], area[0]:area[2]]
        c = similar.calculate(screen, cv2.imread(image))
        self.logger.info("Cal similar with {} : {:.4f}".format(image, c))
        return c


    def click(self, button, delay=(800, 1200)):
        point = (button[0] + random.randint(-button[2], button[2]),
                 button[1] + random.randint(-button[2], button[2]))
        delay = random.randint(delay[0], delay[1])/1000
        r = device_ops.Tap(self.device_id, point)
        time.sleep(delay)
        self.logger.info("Click button:{} | point:{} | delay:{}".format(button, point, delay))
        return True


    def work(self, type='farm', level=6):
        """
        :param type: farm, wood, stone, gold
        :return:
        """
        self.logger.info("Start working, type:{} | level:{}".format(type, level))

        if not device_info.ScreenisLight(self.device_id):
            device_ops.ClickPower(self.device_id)
        # self.open_app()
        if self.in_city():  # 在城内
            self.click(self.home_button)
        self.click(self.search_button)
        if type == 'farm':
            type_button = self.farm_button
            type_level_pic = 'pics/farm_level_685-405-1165-765.png'
        elif type == 'wood':
            type_button = self.wood_button
        else:
            type_button = None

        if self.cal_similar(type_level_pic) < 0.95:
            self.click(type_button)

        # level_reduce_button = (type_button[0]+type_button[3]-195, 580, 10)
        # level_add_button = (type_button[0]+type_button[3]+200, 580, 10)
        # for _ in range(level-1):
        #     self.click(level_add_button, delay=(200, 400))

        search_button = (type_button[0], 700, 40)
        self.click(search_button, delay=(1000,1200))

        center_area = (1200, 515, 60)
        self.click(center_area)


if __name__ == '__main__':
    miner = Miner(device_id='jjypof7xcqzpg6pn')
    miner.work()
    # miner.click(miner.home_button)