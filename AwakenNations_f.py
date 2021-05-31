# -*- coding: utf-8 -*-
# @Author  : LG

from device_ops import device_ops, device_info
from cv_ops import similar
import cv2
import logging
import subprocess
import time
import random

def create_logger(device_id):
    logger = logging.getLogger('{}_logger'.format(device_id))
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler("logs/{}.log".format(device_id))  # 文件处理器
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    console = logging.StreamHandler()  # 控制台处理器
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.addHandler(handler)  # 添加文件输出
    logger.addHandler(console)  # 添加控制台输出
    return logger

def open_app(device_id, logger, app = "com.lilithgames.rok.offical.cn", app_activity = "com.harry.engine.MainActivity"):
    try:
        sub = subprocess.Popen('adb shell pidof {}'.format(app), shell=True, stdout=subprocess.PIPE,
                               universal_newlines=True)
        r = sub.stdout.read()
        if r == '':
            sub = subprocess.Popen(
                'adb -s {} shell am start -n {}/{}'.format(device_id, app, app_activity), shell=True)
            sub.wait(10)
            if sub.returncode == 0:
                logger.info("启动应用")
                time.sleep(10)
                return True
            else:
                return -1
        else:
            logger.info("尝试打开应用，但应用已启动")
            return True
    except:
        return -1

def close_app(device_id, logger, app = "com.lilithgames.rok.offical.cn"):
    try:
        sub = subprocess.Popen('adb -s {} shell pidof {}'.format(device_id, app), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        r = sub.stdout.read()
        if r == '':
            logger.info("尝试关闭应用，但应用未启动")
            return True
        else:
            sub = subprocess.Popen('adb shell am force-stop {}'.format(app), shell=True)
            if sub.returncode == 0:
                logger.info("关闭应用")
                return True
            else:
                return -1
    except:
        return -1

def cal_similar(device_id, logger, image:str, area=None):
    """

    :param image:
    :param area:    xmin ymin xmax ymax
    :return:
    """
    if area is None:
        area = [int(n) for n in image.rstrip('.png').split('_')[-1].split('-')]
    screen = device_ops.ScreenCap(device_id)
    screen = cv2.imread(screen)
    screen = screen[area[1]:area[3], area[0]:area[2]]
    cv2.imwrite('aaa.png', screen)
    c = similar.calculate(screen, cv2.imread(image))
    logger.info("Cal similar with {} : {:.4f}".format(image, c))
    return c

def in_city(device_id, logger):
    home_button = (155, 945, 40)

    screen_pic = device_ops.ScreenCap(device_id)
    home_pic = cv2.imread(screen_pic)[
                 home_button[1] - home_button[2]:home_button[1] + home_button[2],
                 home_button[0] - home_button[2]:home_button[0] + home_button[2],
                 ]    # (155, 945, 45)
    home_map_img = cv2.imread('/home/super/PycharmProjects/untitled/pics/home_map.png')
    home_city_img = cv2.imread('/home/super/PycharmProjects/untitled/pics/home_city.png')
    home_hash = similar.pHash(home_pic)
    map_hash = similar.pHash(home_map_img)
    city_hash = similar.pHash(home_city_img)
    n_map = similar.cmpHash(home_hash, map_hash)
    n_city = similar.cmpHash(home_hash, city_hash)
    logger.info("判断是否在城内, n_map:{} | n_city:{}".format(n_map, n_city))
    if n_map > n_city:  # 当前图标为city图标，在野外，可挖矿
        return False
    else:
        return True

def click(device_id, logger, button, delay=(800, 1200)):
    point = (button[0] + random.randint(-button[2], button[2]),
             button[1] + random.randint(-button[2], button[2]))
    delay = random.randint(delay[0], delay[1])/1000
    r = device_ops.Tap(device_id, point)
    time.sleep(delay)
    logger.info("Click button:{} | point:{} | delay:{}".format(button, point, delay))
    return True

def work(device_id, logger, type='farm', level=6):
    logger.info("Start working, type:{} | level:{}".format(type, level))
    # 自动亮屏
    if not device_info.ScreenisLight(device_id):
        device_ops.ClickPower(device_id)
    # 打开app
    open_app(device_id, logger)
    # 判断是否在城内
    if in_city(device_id, logger):  # 在城内
        home_button = (155, 945, 40)
        click(device_id, logger, home_button)
    # 点击搜索按钮
    search_button = (150, 780, 20)
    click(device_id, logger, search_button)


    if type == 'farm':
        type_button = (925, 910, 50, -5)   # 田         725 1120
        type_level_pic = 'pics/farm_level_685-405-1165-765.png'
        type_pic = 'pics/farm_1140-455-1260-575.png'
    elif type == 'wood':
        type_button = (1200, 910, 50, 0)  # 木         1005 1400
        type_level_pic = 'pics/wood_level_960-405-1440-765.png'
        type_pic = 'pics/wood_1140-455-1260-575.png'
    elif type == 'stone':
        type_button = (1475, 910, 50, 0) # 石         1280 1675
        type_level_pic = 'pics/stone_level_1235-405-1715-765.png'
        type_pic = 'pics/stone_1140-455-1260-575.png'
    elif type == 'gold':
        type_button = (1750, 910, 50, 0)  # 金         1555 1950
        type_level_pic = 'pics/gold_level_1510-405-1990-765.png'
        type_pic = 'pics/gold_1140-455-1260-575.png'
    else:
        logger.error('输入矿物类型不支持 type: {}'.format(type))
        raise ValueError("input type == {}".format(type))

    yanzheng_pic = '/home/super/PycharmProjects/untitled1/pics/验证_1400-440-1710-620.png'
    if cal_similar(device_id, logger, yanzheng_pic) > 0.95:
        logger.error('挂机检查')
        return 9

    # 判断矿物选择页面是否正确，不是当前所采集矿，则点击进行选择
    if cal_similar(device_id, logger, type_level_pic) < 0.95:
        click(device_id, logger, type_button)

    search_button = (type_button[0], 700, 40)
    click(device_id, logger, search_button, delay=(1000,1200))

    # 点击搜索后，查看是否跳转, 存在 无矿情况，导致没有跳转
    if cal_similar(device_id, logger, type_level_pic) > 0.95:
        logger.error('没有资源或其他情况，导致点击搜索后没有跳转')
        return 1  # 无矿物，没跳转
    else:

        # 点击搜索后，等待跳转
        time.sleep(random.randint(1400, 1800) / 1000)
        # 点击屏幕中央矿物图标
        center_area = (1200, 515, 60)
        click(device_id, logger, center_area)

        # 判断并点击采集按钮
        caiji_pic = 'pics/采集按钮_1605-650-1695-740.png'
        if cal_similar(device_id, logger, caiji_pic) < 0.95:
            logger.error('点击资源后，未出现 [采集按钮]')
            return 2  # 矿物正在被采集

        else:
            caiji_button = (1650, 695, 45)
            click(device_id, logger, caiji_button)

            # 创建部队
            chuangjianbudui_pic = 'pics/创建部队按钮_1905-170-1985-250.png'
            if cal_similar(device_id, logger, chuangjianbudui_pic) < 0.95:
                logger.error('点击采集后，未出现 [创建部队按钮]')
                return 3  # 队伍以用完

            else:
                chuangjianbudui_button = (1945, 210, 40)
                click(device_id, logger, chuangjianbudui_button)

                # 行军
                xingjun_pic = 'pics/行军按钮_1575-860-1665-950.png'
                if cal_similar(device_id, logger, xingjun_pic) < 0.95:
                    logger.warning('点击创建部队后，未出现 [行军按钮]')
                    return 4  #
                else:
                    xingjun_button = (1620, 905, 45)
                    click(device_id, logger, xingjun_button)
                    return 0

def run(device_id, types=None):
    logger = create_logger(id)

    if types == None:
        types = ['farm', 'wood', 'stone', 'gold']
    i = 0
    while True:
        if i >= len(types):
            break
        type = types[i]
        r = work(device_id, logger, type)
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
        elif r == 9:
            break
        else:
            break
    close_app(device_id, logger)

if __name__ == '__main__':
    device_id = "jjypof7xcqzpg6pn"
    run(device_id)