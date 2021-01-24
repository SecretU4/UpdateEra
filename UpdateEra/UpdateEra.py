#!/usr/bin/python
# -*- coding: cp949 -*-

from __future__ import print_function

VERSIONSTRING = u'UpdateEra-0.2.1.0 ($Rev: 55 $)' 

import sys

import setting
import batchwork
from utility import *

def usage():
    print(VERSIONSTRING)
    print(
'''
����: UpdateEra ȯ�漳��
    ȯ�漳�� ������ ������ ������ �����ϼ���.
'''
    )

def main():
    if len(sys.argv) < 2:
        usage()
        return 2

    with log.logto(print):
        
        #Load Config
        try:
            config = setting.loadSetting(sys.argv[1])
        except Exception as e:
            log(u'������ �ҷ����� �� �����߽��ϴ�: %s' % sys.argv[1])
            writeExceptionTo(e, log)
            return 3

        import time
        start_time = time.time()
        ret = batchwork.batchwork(config)
        log("�۾� �ð�: %d��" % int(time.time() - start_time))
        return ret




if __name__ == "__main__":
    sys.exit(main())