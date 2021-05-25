# -*- coding: utf-8 -*-
# @Author  : LG

import subprocess


def ScreenCap(device_id, save_path='screen.png'):
    try:
        sub = subprocess.Popen('adb -s {} shell screencap /sdcard/screen.png'.format(device_id), shell=True)
        sub.wait(10)    # 进程等待
        if sub.returncode == 0: # 截图成功
            sub = subprocess.Popen('adb -s {} pull /sdcard/screen.png {}'.format(device_id, save_path), shell=True)
            sub.wait(10)
            if sub.returncode == 0:
                return save_path
        return -1
    except:
        return -1


def ClickHome(device_id):
    try:
        # 点击power键
        sub = subprocess.Popen('adb -s {} shell input keyevent 3'.format(device_id), shell=True)
        sub.wait(10)    # 等待子进程终止
        if sub.returncode == 0:
            return True
        else:
            return -1
    except:
        return -1


def ClickPower(device_id):
    try:
        # 点击power键
        sub = subprocess.Popen('adb -s {} shell input keyevent 26'.format(device_id), shell=True)
        sub.wait(10)    # 等待子进程终止
        if sub.returncode == 0:
            return True
        else:
            return -1
    except:
        return -1


def Swipe(device_id, start_point, end_point, speed):
    try:
        sub = subprocess.Popen('adb -s {} shell input swipe {} {} {} {} {}'.format(device_id,
                                                                                   start_point[0], start_point[1],
                                                                                   end_point[0], end_point[1], speed))
        sub.wait(10)
        if sub.returncode == 0:
            return True
        else:
            return -1
    except:
        return -1


def Tap(device_id, point):
    try:
        sub = subprocess.Popen('adb -s {} shell input tap {} {}'.format(device_id, point[0], point[1]), shell=True)
        sub.wait(10)
        if sub.returncode == 0:
            return True
        else:
            return -1
    except:
        return -1

if __name__ == '__main__':
    Tap('jjypof7xcqzpg6pn', (144, 939))