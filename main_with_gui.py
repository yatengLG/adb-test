# -*- coding: utf-8 -*-
# @Author  : LG

import PySimpleGUI as sg

import logging
import logging.handlers as handlers
import time
from device_ops.device_info import getDevicesId
from AwakenNations_f import run, work, create_logger, close_app
import threading
import os
import json
import datetime

def SearchDevicesFunc(window):
    while True:
        devices = getDevicesId()
        window.write_event_value('-SearchDevices-', devices)
        time.sleep(1)


def SearchDevicesThread():
    threading.Thread(target=SearchDevicesFunc, args=(window,), daemon=True).start()


def AwakenNationsFunc(window, id, logger, types, level):
    i = 0
    while True:
        if i >= len(types):
            break
        t = types[i]
        r = work(id, logger, t, level)
        window.write_event_value('-WORK-', (id , t, level, r))

        if r == 0:      # 0 采集完成；
            continue
        elif r == 1:    # 1 无矿物；
            i += 1
        elif r == 2:    # 2 矿物正在被采集；
            i += 1
        elif r == 3:    # 3 队伍以用完；
            break
        elif r == 4:    # 4 点击创建队伍后，未出现行军按钮
            break
        elif r == 9:    # 验证
            break
        else:
            break
    close_app(id, logger)


def AwakenNationsThread(id, logger, types, level):
    threading.Thread(target=AwakenNationsFunc, args=(window, id, logger, types, level), daemon=True).start()


if __name__ == '__main__':

    logger = logging.getLogger('main_logger')
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # handler = logging.FileHandler("logs/main.log")  # 文件处理器
    handler = handlers.TimedRotatingFileHandler("logs/main.log", when='D', backupCount=8)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    # console = logging.StreamHandler()  # 控制台处理器
    # console.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)  # 添加文件输出
    # logger.addHandler(console)  # 添加控制台输出

    setting_file = os.path.join(os.getcwd(), 'setting.txt')  # 配置文件
    # 加载
    with open(setting_file, 'r') as f:
        settings = json.load(f)

    layout = [[sg.T('')],
              [sg.Frame(layout=[[sg.Checkbox('farm', default='farm'in settings['types'], size=(6, 4), font=('Helvetica 12'), key='-FARM-', enable_events=True)],
                                [sg.Checkbox('wood', default='wood'in settings['types'], size=(6, 4), font=('Helvetica 12'), key='-WOOD-', enable_events=True)],
                                [sg.Checkbox('stone', default='stone'in settings['types'], size=(6, 4), font=('Helvetica 12'), key='-STONE-', enable_events=True)],
                                [sg.Checkbox('gold', default='gold'in settings['types'], size=(6, 4), font=('Helvetica 12'), key='-GOLD-', enable_events=True)],
                                [sg.T('LEVEL', justification='l', size=(6, None), font=('Helvetica 12')), sg.Slider(range=(1, 6), orientation='h', default_value=settings['level'], key='-SETLEVEL-', enable_events=True, size=(10, 20), font=('Helvetica, 12'))],
                                [sg.T('CD(m)', justification='l', size=(6, None), font=('Helvetica 12')), sg.Slider(range=(10, 60), orientation='h', default_value=settings['cd'], key='-SETCD-', enable_events=True, size=(10, None), font=('Helvetica, 12'))],
                                ],
                        title='设置', font=('Helvetica 12')),
               sg.Frame(layout=[[sg.MLine(size=(60, 13), key='-DEVICESINFO-' + sg.WRITE_ONLY_KEY, font=('Helvetica 12')),
                                 sg.MLine(size=(40, 13), key='-DEVICESCD-' + sg.WRITE_ONLY_KEY, font=('Helvetica 12'))],
                                ], title='设备')
               ],
              [sg.Text('优先级:', font=('Helvetica 12'), justification='r', size=(8, None)), sg.Text(key='-TYPES-', size=(30, None), font=('Helvetica 12'))],
              [sg.Output(size=(60, 10), font=('Helvetica 12'))]
              ]

    window = sg.Window('', layout)

    D_cd = {}
    D_er = {}

    SearchDevicesThread()

    while True:
        event, values = window.read()
        window['-TYPES-'].update(' > '.join(settings['types']))
        if not settings['types']:
            print('请选择矿物种类')
            continue
        if event in [sg.WIN_CLOSED]:
            break
        if event == '-FARM-':
            if values['-FARM-']:
                settings['types'].append('farm')
            else:
                try:
                    settings['types'].remove('farm')
                except:
                    pass

        if event == '-WOOD-':
            if values['-WOOD-']:
                settings['types'].append('wood')
            else:
                try:
                    settings['types'].remove('wood')
                except:
                    pass

        if event == '-STONE-':
            if values['-STONE-']:
                settings['types'].append('stone')
            else:
                try:
                    settings['types'].remove('stone')
                except:
                    pass

        if event == '-GOLD-':
            if values['-GOLD-']:
                settings['types'].append('gold')
            else:
                try:
                    settings['types'].remove('gold')
                except:
                    pass

        if event == '-SETLEVEL-':
            settings['level'] = int(values['-SETLEVEL-'])

        if event == '-SETCD-':
            settings['cd'] = int(values['-SETCD-'])

        if event == '-SearchDevicesError-':
            window['-DEVICESINFO-' + sg.WRITE_ONLY_KEY].print("Search device Error", background_color='red')

        if event == '-SearchDevices-':
            devices = values['-SearchDevices-']
            if devices:
                new_devices = [d for d in devices if d not in D_cd.keys()]
                for nd in new_devices:
                    if nd in D_er:
                        continue
                    window['-DEVICESINFO-' + sg.WRITE_ONLY_KEY].print("{} |  add   | {}".format(datetime.datetime.now().time(), nd))
                    AwakenNationsThread(nd, logger, settings['types'], settings['level'])
                    D_cd[nd] = int(time.time())

            remove_devices = [d for d in D_cd if d not in devices]
            for rd in remove_devices:
                window['-DEVICESINFO-' + sg.WRITE_ONLY_KEY].print("{} | remove | {}".format(datetime.datetime.now().time(), rd))
                del D_cd[rd]
                if rd in D_er: del D_er[rd]

        # 刷新设备cd
        cd_info = ["{: ^20} | {: ^20}".format('device', 'cd'),
                   "----------------------------------------"]
        for d, c in D_cd.items():
            cd = int(int(time.time()) - c)
            if cd > settings['cd']*60:
                del D_cd[d]
            cd_info.append('{: <20} | {:<20}'.format(d, settings['cd']*60-cd))
        window['-DEVICESCD-' + sg.WRITE_ONLY_KEY].update('\n'.join(cd_info))


        if event == '-WORK-':
            id, t, level, r = values['-WORK-']
            if r == 9:
                window['-DEVICESINFO-' + sg.WRITE_ONLY_KEY]\
                    .print("{} | error  | {}".format(datetime.datetime.now().time(), id), background_color='red')
                D_er[id] = time.time()

            print("device: {} | type: {} | r: {}".format(id ,t ,r))

    with open(setting_file, 'w') as f:
        json.dump(settings, f)
    window.close()



    # # 设备计时
    # record = {}
    # # 进程池
    # pool = Pool(processes=10)
    #
    # while True:
    #     ids = getDevicesId()
    #     if ids == -1:
    #         logger.info('未扫描到新设备')
    #         time.sleep(10)
    #         continue
    #     now_ids = record.keys()
    #     new_ids = [id for id in ids if id not in now_ids]
    #     logger.info('当前cd设备： {}'.format(" | ".join(["{}:{}".format(k,v) for k,v in record.items()])))
    #
    #     logger.info('扫描到新设备： {}'.format(' | '.join(new_ids)))
    #
    #     for id in new_ids:
    #
    #         pool.apply_async(func=run, args=[id])
    #
    #         record[id] = 300
    #         logger.info('添加任务： {}'.format(id))
    #     time.sleep(10)
    #     record = {k:v-10 for k,v in record.items()}
    #     for k,v in record.items():
    #         if v <= 0:
    #             del record[k]
    #             logger.info('删除任务： {}')
    #
    #
    # pool.close()
    # pool.join()