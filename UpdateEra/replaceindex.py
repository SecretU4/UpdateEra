#!/usr/bin/python
# -*- coding: cp949 -*-

import re
import os
import translate
import filehandler
from utility import *

class ReplaceIndexError(Exception):
    pass

def splitEOL(s):
    """return string-without-eol, eol"""
    if s.endswith(u'\r\n'):
        return s[:-2], u'\r\n'
    elif s.endswith(u'\n'):
        return s[:-1], u'\n'
    else:
        return s, u''

def buildReplaceIndex(f_replaceindex, ri_encoding, ri_autodetect):
    """
    return ReplaceIndex [(re, replace)]
    raise ReplaceIndexError for non-IO error
    """
    
    #def buildReplaceIndex_TSV(lines, default_wordwrap = False):
    #    """CSV format handler"""
    #    import csv
    #    pattern = []

    #    for l in csv.reader(lines, ):
    #        if len(l) < 2:
    #            continue
    #        
    #        find = l[0]
    #        replace = l[1]

    #        find = re.escape(find)
    #        if default_wordwrap:
    #            find = u'\\b' + find + '\\b'
    #        pattern.append((find, replace))
    #    return [(re.compile(find, re.UNICODE), replace) for find, replace in pattern]

    def buildReplaceIndex_SIMPLESRS(lines):
        """SRS format handler"""
        
        lines = [splitEOL(s)[0] for s in lines]
        pattern = []
        n = 0
        find = u''
        replace = u''
        regex = False
        sortbylength = False
        wordwrap = False

        trim = lambda x: x

        if len(lines) != 0:
            l = lines[0].upper()
            #flag 처리
            if l.startswith(u'[-')  and l.endswith(u'-]'):
                n = 1
                if l.find('[-WORDWRAP-]') != -1:
                    wordwrap = True
                if l.find('[-TRIM-]') != -1:
                    trim  = lambda x: x.strip()
                if l.find('[-REGEX-]') != -1:
                    regex = True
                if l.find('[-SORT-]') != -1:
                    sortbylength = True
                if regex and sortbylength:
                    raise ReplaceIndexError(u'[-REGEX-] 및 [-SORT-]는 같이 쓰일 수 없습니다.' % n)

        while n < len(lines):
            l = trim(lines[n])
            if l == u'':
                find = u''
                replace = u''
            else:
                if find == u'':
                    find = l
                elif replace == u'':
                    replace = l

                    pattern.append((find, replace))

                    find = u''
                    replace = u''
            n += 1

        if sortbylength:
            pattern.sort(key=lambda x:len(x[0]), reverse=True)
        if not regex:
            pattern = [(re.escape(find), replace) for find, replace in pattern]
        if wordwrap:
            pattern = [(u'\\b' + find + '\\b', replace) for find, replace in pattern]
        #return pattern
        return [(re.compile(find, re.UNICODE), replace) for find, replace in pattern]

    def buildReplaceIndex_SRS(lines):
        """SRS format handler"""
        lines = [splitEOL(s)[0] for s in lines]
        pattern = []
        n = 0
        while n < len(lines):
            if lines[n] == u'[Search]':
                if lines[n + 2] != u'[Replace]':
                    raise ReplaceIndexError(u'잘못된 SRS 포맷입니다. (line %d)' % n)
                find = lines[n + 1]
                replace = lines[n + 3]
                n += 3

                if find == '':
                    continue

                find = re.escape(find)
                pattern.append((find, replace))
            n += 1
        return [(re.compile(find, re.UNICODE), replace) for find, replace in pattern]
    def buildReplaceIndex_RICHAIN(lines, ri_encoding, ri_autodetect):
        """RICHAIN format handler"""
        lines = [splitEOL(s)[0] for s in lines]

        ri = []

        for i in lines:
            fn = i.strip()
            if fn == "":
                continue

            f_ri = filehandler.open(fn, False, ri_encoding, ri_autodetect)
            ri.extend(buildReplaceIndex(f_ri, ri_encoding, ri_autodetect))
 
        return ri



    #format 검증

    lines = f_replaceindex.readlines()
    fnroot, ext = os.path.splitext(f_replaceindex.name)

    ri = None
    if ext.upper() == '.SRS':
        ri = buildReplaceIndex_SRS(lines)
    elif ext.upper() == '.SIMPLESRS':
        ri = buildReplaceIndex_SIMPLESRS(lines)
    elif ext.upper() == '.RICHAIN':
        ri = buildReplaceIndex_RICHAIN(lines, ri_encoding, ri_autodetect)
    else:
        raise ReplaceIndexError(u'%s가 무슨 포맷인지 알 수 없습니다.' % f_replaceindex.name) #unknown format
    return ri



def buildReplaceIndexWorker(f_replaceindex, ri_encoding, ri_autodetect):
    """
    return ReplaceIndexWorker
    raise ReplaceIndexError for non-IO error
    """
    
    return translate.CachedWorker(ReplaceIndexWorker(buildReplaceIndex(f_replaceindex, ri_encoding, ri_autodetect)), 10000) #cache size 필요시 조정


#Hash-based RI Agent

class ReplaceIndexWorker(object):
    def __init__(self, replaceindex):
        '''여긴 replaceindex != None이어야 한다. 적용 안할거면 밖에서 처리할것'''
        self.replaceindex = replaceindex        

    def __call__(self, x):
        for prog, repl in self.replaceindex:
            x = prog.sub(repl, x)
        return x