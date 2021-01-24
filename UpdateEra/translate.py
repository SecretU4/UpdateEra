#!/usr/bin/python
# -*- coding: cp949 -*-

import seslib
from utility import *

#Error Definition



#LineWorker Definition

class LineWorker(object):
    def __call__(self, x):
        return x

class ChainWorker(LineWorker, list):
    def __init__(self, *args):
        LineWorker.__init__(self)
        list.__init__(self, *args)
    def __call__(self, x):
        for i in self:
            x = i(x)
        return x

class CachedWorker(LineWorker):
    def __init__(self, worker, cache_size):
        LineWorker.__init__(self)
        self.worker = worker
        self.cache = LRU(cache_size)

    def __call__(self, x):
        if x in self.cache:
            return self.cache[x]
        else:
            v = self.worker(x)
            self.cache[x] = v
            return v

#Error definitions

class TranslateError(Exception):
    pass

class LineMatchError(TranslateError):
    pass

class DictMatchError(TranslateError):
    pass

#Utility functions

def __getlines(f):
    try:
        return f.readlines()
    except:
        raise TranslateError(u'%s �б� ���� (���ڵ��� Ȯ���ϼ���)' % f.name)

#Main functions

class PreprocessWorker(LineWorker):
    def __init__(self, config):
        self.trim_prefix = config['trim_prefix']
    def __call__(self, s):
        """return prefix, rest, postfix"""

        if s.endswith(u'\r\n'):
            index_postfix = len(s) - 2
        elif s.endswith(u'\n'):
            index_postfix = len(s) - 1
        else:
            index_postfix = len(s)

        index_prefix = 0
        for i in s[:index_postfix]:
            if not (i in self.trim_prefix):
                break
            index_prefix += 1

        return s[:index_prefix], s[index_prefix:index_postfix], s[index_postfix:]

class LineRefWorker(LineWorker):
    def __init__(self, dictionary):
        self.d = dictionary
        self.num_translated_line = 0
    def __call__(self, x):
        if x in self.d:
            self.num_translated_line += 1
            return self.d[x]
        return -1

def updateFile(f_oo, f_ot, f_no, f_nt, riw = None, trim_prefix = '', force_hash = False):
    """
    raise TranslateError
    return isChanged
    """

    #Prefix SES apply callback class
    class PrefixAccumulator(object):
        def __init__(self, fallback=None):
            self.result = u''
            self.fallback=fallback
            self.isFailed = False
        def __call__(self, seq, index, total_position):
            if self.isFailed:
                return
            try:
                self.result += seq[index]
            except:
                self.isFailed = True
                self.result = self.fallback
                
                    

    config = {'riw': riw, 'trim_prefix': trim_prefix, 'force_hash': force_hash}

    try:
        #Phase 0: ���� �б� (TODO: Phase 1/2�� ����? - Space requirement)

        log(u'$���� �б�')

        l_oo = __getlines(f_oo)
        l_ot = __getlines(f_ot)
        l_no = __getlines(f_no)


        #Phase 1: Preprocessing (prefix and postfix)

        log(u'$Prefix, Postfix ��ó��')

        pw = PreprocessWorker(config)

        l_oo = map(pw, l_oo)
        l_ot = map(pw, l_ot)
        l_no = map(pw, l_no)
        
        #Phase 2: ���� ��ȹ ����

        #mode enum
        MODE_COPY = 1
        MODE_HASH_ONLY = 2
        MODE_SES = 3

        def buildplan(config, f_oo, f_ot, f_no):
            """
            return mode, lrw, riw
            """
            force_hash = config['force_hash']
            riw = config['riw']

            #���μ� ��ġ Ȯ��
            if len(l_oo) != len(l_ot):
                raise LineMatchError(u'���� �� ����ġ: %s, %s' % (f_oo.name, f_ot.name))

            #mode Ȯ�� �� oorest -> n(oo/ot) dictionary ����

            mode = MODE_HASH_ONLY
            changed = len(l_oo) != len(l_no) # �ϴ� ���μ��� �ȸ����� �翬�� �ٲ��. ���� len�� ���ٴ� Ȯ���� ����
            dictionary = {}
            dictionary_exclude = set() #���� �浹�� �������� �������� ���
            for n in range(len(l_oo)):

                ooprefix, oorest, oopostfix = l_oo[n]
                otprefix, otrest, otpostfix = l_ot[n]

                #���濩�� üũ
                if (not changed):
                    #�ϴ� ���μ��� ��ġ�ϹǷ� [n]�� ����
                    noprefix, norest, nopostfix = l_no[n]
                    if ooprefix != noprefix or oorest != norest:
                        changed = True

                if oorest in dictionary:
                    old_otn = dictionary[oorest]
                    old_otprefix, old_otrest, old_otpostfix = l_ot[old_otn]

                    if old_otrest != otrest:
                        if force_hash:
                            log(u'(*���*) ���� ���� �浹: ������ %s�� ���������� %s �� %s �ΰ����� ��ȯ�˴ϴ�. (ForceHash: ���ڷ� �����˴ϴ�.)' % (oorest, old_otrest, otrest))
                        else:
                            mode = MODE_SES
                            log(u'���� ���� �浹: ������ %s�� ���������� %s �� %s �ΰ����� ��ȯ�˴ϴ�. (�ش� ������ ���õ˴ϴ�)' % (oorest, old_otrest, otrest))
                            dictionary_exclude.add(oorest)
                else:
                    dictionary[oorest] = n


            #Ȯ�ε� mode�� ���� ��ó��

            if not changed:
                mode = MODE_COPY
            elif mode == MODE_SES:
                for i in dictionary_exclude:
                    del dictionary[i]

            #Dictionary reference worker
            lrw = LineRefWorker(dictionary)

            #riw == None�̸� identity function ����
            if riw == None:
                riw = lambda x:x

            return mode, lrw, riw

        log(u'$���� ��ȹ ����')

        mode, lrw, riw = buildplan(config, f_oo, f_ot, f_no)

        if mode == MODE_COPY:
            log(u' -> ������ �� �Ź����� ���� ���� �������� �����ϴ�.')
        elif mode == MODE_SES:
            log(u' -> SES�� �����մϴ�.')
        else: #mode == MODE_HASH_ONLY:
            log(u' -> Hash ������ ����մϴ�.')

        #Phase 3: ����

        log(u'$���� ��')

        if mode == MODE_COPY:
            #MODE_COPY
            #when ooprefix == noprefix && oorest == norest for all n (eol postfix ���� ����)
            # -> l_ot ��� (otrest�� riw�� ����)
            for otprefix, otrest, otpostfix in l_ot:
                f_nt.write(otprefix)
                f_nt.write(riw(otrest))
                f_nt.write(otpostfix)
            return False

        elif mode == MODE_HASH_ONLY:
            #MODE_HASH_ONLY
            #when no dictionary collision happens OR force_hash is enabled
            # -> l_no�� ����
            #    1) match�� ������: norest�� lrw �� riw ����, ooprefix->noprefix ses�� otprefix�� ���� �� no ���
            #    2) match�� ������: l_no ��� (norest�� riw�� ����)

            #n(oo/ot) -> ses cache

            for n in range(len(l_no)):
                noprefix, norest, nopostfix = l_no[n]

                otn = lrw(norest)
                
                if otn == -1: #no match
                    f_nt.write(noprefix)
                    f_nt.write(riw(norest))
                    f_nt.write(nopostfix)
                else: #match
                    ses = seslib.ses(l_oo[otn][0], noprefix)
                    #Prefix ����
                    pa = PrefixAccumulator(fallback=noprefix)
                    seslib.apply(ses, l_ot[otn][0], noprefix, pa)
                    f_nt.write(pa.result)
                    f_nt.write(riw(l_ot[otn][1]))
                    f_nt.write(nopostfix)

            log(u'�� %d �� �� %d ���� ġȯ�Ǿ� ����Ǿ����ϴ�.' % (len(l_no), lrw.num_translated_line))
            return True
        
        else: #mode == MODE_SES:
            #MODE_SES
            #when dictionary collision happens
            # -> [oorest]->[norest] ses�� [otrest]�� ����
            #    1) otrest ��� sequence: ooprefix->noprefix ses�� otprefix�� ����, otrest�� riw ���� �� ot ���
            #    2) command i: dictionary Ȯ��
            #       2.1) match�� ������: norest�� lrw �� riw ����, ooprefix->noprefix ses�� otprefix�� ���� �� no ���
            #       2.2) match�� ������: l_no ��� (norest�� riw�� ����)
            #    3) command d: -

            #SES ����
            seq_oorest = map(lambda x:x[1], l_oo)
            seq_norest = map(lambda x:x[1], l_no)

            class SesModeApplier(object):
                def __init__(self, l_oo, l_ot, l_no, lrw, riw, f_nt):
                    #line no -> ses cache
                    self.l_oo = l_oo
                    self.l_ot = l_ot
                    self.l_no = l_no
                    self.lrw = riw
                    self.riw = riw
                    self.f_nt = f_nt
                def __call__(self, seq, otn, total_position):
                    if seq == self.l_ot:
                        #    1) otrest ��� sequence: ooprefix->noprefix ses�� otprefix�� ����, otrest�� riw ���� �� no ���
                        ses = seslib.ses(self.l_oo[otn][0], self.l_no[total_position][0])
                        #Prefix ����
                        pa = PrefixAccumulator(fallback=self.l_no[total_position][0])
                        seslib.apply(ses, self.l_ot[otn][0], self.l_no[total_position][0], pa)
                        self.f_nt.write(pa.result)
                        self.f_nt.write(self.riw(self.l_ot[otn][1]))
                        self.f_nt.write(self.l_no[total_position][2])
                    else: 
                        #    2) command i: dictionary Ȯ��
                        #       2.1) match�� ������: norest�� lrw �� riw ����, ooprefix->noprefix ses�� otprefix�� ���� �� no ���
                        #       2.2) match�� ������: l_no ��� (norest�� riw�� ����)
                        noprefix, norest, nopostfix = self.l_no[total_position]
                        otn = lrw(norest)
                
                        if otn == -1: #no match
                            self.f_nt.write(noprefix)
                            self.f_nt.write(riw(norest))
                            self.f_nt.write(nopostfix)
                        else: #match
                            ses = seslib.ses(self.l_oo[otn][0], noprefix)
                            #Prefix ����
                            pa = PrefixAccumulator()
                            seslib.apply(ses, self.l_ot[otn][0], noprefix, pa)
                            self.f_nt.write(pa.result)
                            self.f_nt.write(self.riw(self.l_ot[otn][1]))
                            self.f_nt.write(nopostfix)

            count_i, count_d = seslib.apply(seslib.ses(seq_oorest, seq_norest), l_ot, l_no, SesModeApplier(l_oo, l_ot, l_no, lrw, riw, f_nt))
            
            if count_i == 0 and count_d == 0:
                log(u'�Ϻ� ���� Prefix�� ��ȭ�� ������, ��ü �������� ���̰� �����ϴ�.')
            else:
                log(u'�� %d ���� �߰��ǰ� %d ���� �����Ǿ� ����Ǿ����ϴ�.' % (count_i, count_d))
                log(u'�߰��� %d �� �� %d ���� ġȯ�Ǿ� ����Ǿ����ϴ�.' % (count_i, lrw.num_translated_line))

            return True
    except:
#        import traceback
#        traceback.print_exc()
        log(u'*** ������ ���� �ߴ�! ***')
        raise

def copyFile(f_src, f_dst, riw, trim_prefix):

    config = {'riw': riw, 'trim_prefix': trim_prefix}

    try:
        #Phase 0: ���� �б� (TODO: Phase 1/2�� ����? - Space requirement)

        log(u'$���� �б�')

        l_src = __getlines(f_src)

        #Phase 1: Preprocessing (prefix and postfix)

        log(u'$Prefix, Postfix ��ó��')

        pw = PreprocessWorker(config)
        l_src = map(pw, l_src)

        #riw == None�̸� identity function ����
        if riw == None:
            riw = lambda x:x
        
        #Phase 2: ����

        log(u'$���� ��')

        for srcprefix, srcrest, srcpostfix in l_src:
            f_dst.write(srcprefix)
            f_dst.write(riw(srcrest))
            f_dst.write(srcpostfix)
    except:
        log(u'*** ������ ���� �ߴ�! ***')
        raise