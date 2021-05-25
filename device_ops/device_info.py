# -*- coding: utf-8 -*-
# @Author  : LG

import subprocess


def getDevicesId():
    sub = subprocess.Popen('adb devices', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    sub.wait(10)
    devices = sub.stdout.read().splitlines()
    ids = []
    if len(devices) >2: # 第一行无效内容, 最后一行空行
        for device in devices:
            if device.startswith('List'):
                continue
            elif device == '':
                continue
            else:
                ids.append(device.split('\t')[0])
        return ids
    else:
        return -1


def getScreenSize(device_id):
    try:
        out = subprocess.Popen('adb -s {} shell wm size'.format(device_id), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        out.wait(10)
        line1 = out.stdout.read().splitlines()[0]
        w, h = line1.lstrip('Physical size: ').split('x')
        return int(w), int(h)
    except:
        return -1


def ScreenisLight(device_id):
    try:
        sub = subprocess.Popen('adb -s {} shell dumpsys window policy | grep screenState'.format(device_id), shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        sub.wait(10)
        out = sub.stdout.read().splitlines()[0]
        if out.endswith('ON'):
            return True
        elif out.endswith('OFF'):
            return False
        else:
            return -1
    except:
        return -1

if __name__ == '__main__':
    ids = getDevicesId()
    print(ids)
