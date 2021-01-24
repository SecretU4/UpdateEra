#!/usr/bin/python
# -*- coding: utf-8 -*-

#인코딩 관련 유틸리티 모듈

import chardet
import io
import sys
from utility import *


def isAvailableAutodetectMode(autodetect):
    ''' 자동감지로 쓸 수 있는가 '''
    return autodetect == 'no' or autodetect == 'chardet' or autodetect == 'mskanji' or autodetect == 'safedetect'

def open(fn, write, codecname, autodetect):
    if write or (autodetect == 'no'):
        return io.open(fn, {True: 'w', False: 'r'}[write], encoding=codecname)
    elif autodetect == 'chardet' or autodetect == 'mskanji' or autodetect == 'safedetect':
        #일단 읽고본다. 
        # 1. chardet 돌려보고 결과가 나오면 그대로 사용
        # 2. 안나오면 기본 codecname으로 fallback
        with io.open(fn, 'rb') as f:
            buf = f.read()

        try:
            if autodetect == 'safedetect':
                #초반 BOM만 읽으면 끝. 못읽으면 mskanji 고정
                result = chardet.detect(buf[:10])
            else:
                result = chardet.detect(buf)
            confidence = result.get('confidence', 0.0)
            encoding = result.get('encoding', None)
            if encoding == None or confidence < 0.1:
                encoding = codecname
            elif encoding.upper().startswith('UTF-8'):
                encoding = 'utf-8-sig' #UTF-8 -> UTF-8-SIG (BOM)
            elif encoding.upper().startswith('UTF-16'):
                    encoding = 'UTF-16' #UTF-16LE -> UTF-16 (BOM)
            elif autodetect == 'safedetect':
                if not encoding.upper().startswith('UTF'):
                    encoding = codecname
            elif autodetect == 'mskanji' and encoding.upper() == 'SHIFT_JIS':
                encoding = 'mskanji'
        except:
            encoding = codecname

        #일부 코드가 파일명을 필요로 하므로
        file = io.BytesIO(buf)
        setattr(file, 'name', fn)

        log(u' - 인코딩 (%s): %s' % (fn, encoding))

        return io.TextIOWrapper(file, encoding=encoding)
    else:
        raise LookupError(u'unknown autodetect mode: %s' % autodetect)

