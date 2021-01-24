#!/usr/bin/python
# -*- coding: cp949 -*-

#���ڵ� ���� ��ƿ��Ƽ ���

import chardet
import io
import sys
from utility import *


def isAvailableAutodetectMode(autodetect):
    ''' �ڵ������� �� �� �ִ°� '''
    return autodetect == 'no' or autodetect == 'chardet' or autodetect == 'mskanji' or autodetect == 'safedetect'

def open(fn, write, codecname, autodetect):
    if write or (autodetect == 'no'):
        return io.open(fn, {True: 'w', False: 'r'}[write], encoding=codecname)
    elif autodetect == 'chardet' or autodetect == 'mskanji' or autodetect == 'safedetect':
        #�ϴ� �а���. 
        # 1. chardet �������� ����� ������ �״�� ���
        # 2. �ȳ����� �⺻ codecname���� fallback
        with io.open(fn, 'rb') as f:
            buf = f.read()

        try:
            if autodetect == 'safedetect':
                #�ʹ� BOM�� ������ ��. �������� mskanji ����
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

        #�Ϻ� �ڵ尡 ���ϸ��� �ʿ�� �ϹǷ�
        file = io.BytesIO(buf)
        setattr(file, 'name', fn)

        log(u' - ���ڵ� (%s): %s' % (fn, encoding))

        return io.TextIOWrapper(file, encoding=encoding)
    else:
        raise LookupError(u'unknown autodetect mode: %s' % autodetect)

