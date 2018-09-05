# -*- coding: utf-8 -*-

######################
# Author : jiaiqing
# Data : 2018-08-05
# Brief : 用于自动检查新信息的爬虫
######################

import time
import logging
import logging.handlers

from SQ12345 import *


# Init

UnicomKeywords = [
   '测试1'
]

UnicomSpecialKeywords = [
   '测试1'
]


WebList = []
WebList.append(SQ12345('宿迁12345问政论坛', 'SQ12345_data', 1000004, UnicomKeywords, UnicomSpecialKeywords))

LOG_FILE = "Debug.log"
#  logging.basicConfig(
#      filename='%s.log'%(time.strftime("%Y_%m_%d", time.localtime())), level=logging.WARNING,
#      format='%(asctime)s  :  %(message)s')

logger = logging.getLogger()
fh = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=7)
formatter = logging.Formatter('%(asctime)s  :  %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logging.critical('Program Start!\n')
while True:
    #logging.warning('Start a new loop~')
    print('Start a new loop~')

    Now_time = time.strftime("%H",time.localtime(time.time()))
    if int(Now_time) > 21 or int(Now_time) < 8:
        time.sleep(300)
        print('Current time between 22:00 and 8:00, sleep:300 seconds!')
        continue

    for web in WebList:
        try:
            #logging.warning('************************')
            web.GET()

        except Exception as err:
            logging.error('Unexpected ERROR!!!!!!')
            logging.error(repr(err))
            # traceback.print_exc()

            web.err += 1
            if 4 == web.err:
                try:
                    web.ReportErrStatus(repr(err), True)
                    logging.warning('Send Wchat Error Report.')
                except:
                    logging.critical('Send Wchat Error Report Error!!!!!')
        else:
            if web.err >= 4:
                try:
                    web.ReportErrStatus('', False)
                    logging.warning('Send Wchat Recovery Report.')
                except:
                    logging.critical('Send Wchat Recovery Report Error!!!!!')
            web.err = 0

        finally:
            web.Update()

    #logging.warning('************************')
    #logging.warning('End of a loop~\n')
    time.sleep(200)

logging.critical('Program End!\n')

