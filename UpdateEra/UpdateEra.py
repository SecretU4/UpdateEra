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
사용법: UpdateEra 환경설정
    환경설정 파일의 포맷은 도움말을 참조하세요.
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
            log(u'설정을 불러오는 데 실패했습니다: %s' % sys.argv[1])
            writeExceptionTo(e, log)
            return 3

        import time
        start_time = time.time()
        ret = batchwork.batchwork(config)
        log("작업 시간: %d초" % int(time.time() - start_time))
        return ret




if __name__ == "__main__":
    sys.exit(main())