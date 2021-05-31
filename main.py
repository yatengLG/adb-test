# -*- coding: utf-8 -*-
# @Author  : LG


import logging
import time
from device_ops.device_info import getDevicesId
from AwakenNations_f import run, create_logger
from multiprocessing import Pool

if __name__ == '__main__':

    logger = logging.getLogger('main_logger')
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler("logs/main.txt")  # 文件处理器
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    console = logging.StreamHandler()  # 控制台处理器
    console.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)  # 添加文件输出
    logger.addHandler(console)  # 添加控制台输出

    record = {}

    pool = Pool(processes=10)

    while True:
        ids = getDevicesId()
        if ids == -1:
            logger.info('未扫描到新设备')
            time.sleep(10)
            continue
        now_ids = record.keys()
        new_ids = [id for id in ids if id not in now_ids]
        logger.info('当前cd设备： {}'.format(" | ".join(["{}:{}".format(k,v) for k,v in record.items()])))

        logger.info('扫描到新设备： {}'.format(' | '.join(new_ids)))

        for id in new_ids:

            pool.apply_async(func=run, args=[id])

            record[id] = 300
            logger.info('添加任务： {}'.format(id))
        time.sleep(10)
        record = {k:v-10 for k,v in record.items()}
        for k,v in record.items():
            if v <= 0:
                del record[k]
                logger.info('删除任务： {}')


    pool.close()
    pool.join()