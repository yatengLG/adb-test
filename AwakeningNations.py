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
    def __init__(self, device_id, time_out=300):
        self.start_time = time.time()
        self.time_out = time_out

        self.logger = logging.getLogger('{}_logger'.format(device_id))
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
        self.app = "com.lilithgames.rok.offical.cn"
        self.app_activity = "com.harry.engine.MainActivity"

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
            sub = subprocess.Popen('adb shell pidof {}'.format(self.app), shell=True, stdout=subprocess.PIPE,
                                   universal_newlines=True)
            r = sub.stdout.read()
            if r == '':
                sub = subprocess.Popen('adb -s {} shell am start -n {}/{}'.format(self.device_id, self.app, self.app_activity), shell=True)
                sub.wait(10)
                if sub.returncode == 0:
                    self.logger.info("启动应用")
                    time.sleep(10)
                    return True
                else:
                    return -1
            else:
                self.logger.info("尝试打开应用，但应用已启动")
                return True
        except:
            return -1

    def close_app(self):
        try:
            sub = subprocess.Popen('adb shell pidof {}'.format(self.app), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            r = sub.stdout.read()
            if r == '':
                self.logger.info("尝试关闭应用，但应用未启动")
                return True
            else:
                sub = subprocess.Popen('adb shell am force-stop {}'.format(self.app), shell=True)
                if sub.returncode == 0:
                    self.logger.info("关闭应用")
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
        screen = cv2.imread(screen)
        screen = screen[area[1]:area[3], area[0]:area[2]]
        cv2.imwrite('aaa.png', screen)
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

        # 自动亮屏
        if not device_info.ScreenisLight(self.device_id):
            device_ops.ClickPower(self.device_id)

        self.open_app()     # 启动app后，由于存在更新提醒等复杂情况，建议手动进入游戏后 进行连接；后续可优化
        if self.in_city():  # 在城内
            self.click(self.home_button)
        self.click(self.search_button)
        if type == 'farm':
            type_button = self.farm_button
            type_level_pic = 'pics/farm_level_685-405-1165-765.png'
            type_pic = 'pics/farm_1140-455-1260-575.png'
        elif type == 'wood':
            type_button = self.wood_button
            type_level_pic = 'pics/wood_level_960-405-1440-765.png'
            type_pic = 'pics/wood_1140-455-1260-575.png'
        elif type == 'stone':
            type_button = self.stone_button
            type_level_pic = 'pics/stone_level_1235-405-1715-765.png'
            type_pic = 'pics/stone_1140-455-1260-575.png'
        elif type == 'gold':
            type_button = self.gold_button
            type_level_pic = 'pics/gold_level_1510-405-1990-765.png'
            type_pic = 'pics/gold_1140-455-1260-575.png'
        else:
            self.logger.error('输入矿物类型不支持 type: {}'.format(type))
            raise ValueError("input type == {}".format(type))

        # 判断矿物选择页面是否正确，不是当前所采集矿，则点击进行选择
        print("点击搜索", self.cal_similar(type_level_pic))
        if self.cal_similar(type_level_pic) < 0.95:
            self.click(type_button)

        ## 采矿等级调整，建议预先手动设定好
        # level_reduce_button = (type_button[0]+type_button[3]-195, 580, 10)
        # level_add_button = (type_button[0]+type_button[3]+200, 580, 10)
        # for _ in range(level-1):
        #     self.click(level_add_button, delay=(200, 400))

        search_button = (type_button[0], 700, 40)
        self.click(search_button, delay=(1000,1200))

        # 点击搜索后，查看是否跳转, 存在 无矿情况，导致没有跳转
        print("点击搜索", self.cal_similar(type_level_pic))
        if self.cal_similar(type_level_pic) > 0.95:
            self.logger.error('没有资源或其他情况，导致点击搜索后没有跳转')
            return 1    # 无矿物，没跳转
        else:

            # 点击搜索后，等待跳转
            time.sleep(random.randint(1400, 1800)/1000)
            # r = self.cal_similar(type_pic)
            # sleep_time = 0
            # while r < 0.95:
            #     self.logger.info('Wait 500ms, r:{}'.format(r))
            #     time.sleep(0.5)
            #     r = self.cal_similar(type_pic)
            #     sleep_time += 0.5
            #     if sleep_time > 10:
            #         self.logger.error('检测进入死循环，程序跳出')
            #         break

            # 点击屏幕中央矿物图标
            center_area = (1200, 515, 60)
            self.click(center_area)

            # 判断并点击采集按钮
            caiji_pic = 'pics/采集按钮_1605-650-1695-740.png'
            print("采集按钮", self.cal_similar(caiji_pic))
            if self.cal_similar(caiji_pic) < 0.95:
                self.logger.error('点击资源后，未出现 [采集按钮]')
                return 2 # 矿物正在被采集

            else:
                caiji_button = (1650, 695, 45)
                self.click(caiji_button)

                # 创建部队
                chuangjianbudui_pic = 'pics/创建部队按钮_1905-170-1985-250.png'
                print("创建部队按钮", self.cal_similar(chuangjianbudui_pic))
                if self.cal_similar(chuangjianbudui_pic) < 0.95:
                    self.logger.error('点击采集后，未出现 [创建部队按钮]')
                    return 3    # 队伍以用完

                else:
                    chuangjianbudui_button = (1945, 210, 40)
                    self.click(chuangjianbudui_button)

                    # 行军
                    xingjun_pic = 'pics/行军按钮_1575-860-1665-950.png'
                    print("行军按钮", self.cal_similar(xingjun_pic))
                    if self.cal_similar(xingjun_pic) < 0.95:
                        self.logger.warning('点击创建部队后，未出现 [行军按钮]')
                        return 4 #
                    else:
                        xingjun_button = (1620, 905, 45)
                        self.click(xingjun_button)
                        return 0

    def run(self, types=None):
        if types == None:
            types = ['farm', 'wood', 'stone', 'gold']
        i = 0
        while (time.time() - self.start_time) < self.time_out:
            if i >= len(types):
                break
            type = types[i]
            r = self.work(type)
            if r == 0:      # 0 采集完成；
                continue
            elif r == 1:    # 1 无矿物；
                i += 1
            elif r == 2:    # 2 矿物正在被采集；
                i += 1
            elif r == 3:    # 3 队伍以用完；
                break
            elif r == 4:    # 4 点击创建队伍后，未出现行军按钮
                continue
            else:
                break
        self.close_app()


if __name__ == '__main__':
    miner = Miner(device_id='jjypof7xcqzpg6pn')
    # miner.work('wood')
    # miner.click(miner.home_button)
    miner.close_app()