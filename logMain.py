import sys
import os
import time
import threading

if __name__ == '__main__':
    import logging2

    logging2.init("logMain", "DEBUG")

    teststr = "22222"

    while True:
        logging2.debug('this is a debug log test [%s] ', teststr)
        logging2.info('this is a info log test [%s] [%s]', teststr, teststr)
        logging2.warn('this is a warn log test')
        logging2.error('this is a error log test')
        # time.sleep(0.1)

    print(threading.enumerate())

    print('press ctrl_c to exit')
