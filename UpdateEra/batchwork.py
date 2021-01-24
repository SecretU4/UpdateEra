#!/usr/bin/python
# -*- coding: cp949 -*-

import os
import collections
import shutil

from utility import *
import filehandler
import translate
import replaceindex


#Exception definitions




####################
#Directory related utility functions
####################

def dirFileList(rootname):
    """
    raise Exception when rootname is invalid directory or read fails
    """
    if not os.path.isdir(rootname):
        raise IOError(u'%s 디렉토리가 존재하지 않습니다.' % rootname)
    rootpath = os.path.abspath(unicode(rootname))

    ret = set()
    for dirpath, dirs, files in os.walk(rootname):
        for filename in files:
            filepath = os.path.join(dirpath, filename)
            relpath = os.path.relpath(filepath, rootpath)
            ret.add(relpath.upper())

    return ret

def ensureDir(f):
    """
    raise Exception when making fails
    """
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

####################
#File handlers
####################

#Actions

class FileActionItem(object):
    def __init__(self, handler, description):
        self.handler = handler
        self.description = description

def isAvailableAction(case, action):
    ''' 자동감지로 쓸 수 있는가 '''
    if action == 'update' or action == 'update-hash':
        return case == 1
    elif action == 'copy-oo':
        return case == 1 or case == 2 or case == 3 or case == 4
    elif action == 'copy-ot':
        return case == 1 or case == 2 or case == 5 or case == 6
    elif action == 'copy-no':
        return case == 1 or case == 3 or case == 5 or case == 7
    elif action == '':
        return True
    else:
        return False

def update_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary, force_hash = False):
    oo_basepath, oo_encoding, oo_autodetect = config['OO_Directory'], config['OO_Encoding'], config['OO_Autodetect']
    ot_basepath, ot_encoding, ot_autodetect = config['OT_Directory'], config['OT_Encoding'], config['OT_Autodetect']
    no_basepath, no_encoding, no_autodetect = config['NO_Directory'], config['NO_Encoding'], config['NO_Autodetect']
    nt_basepath, nt_encoding, nt_autodetect = config['NT_Directory'], config['NT_Encoding'], config['NT_Autodetect']

    oo_path = os.path.join(oo_basepath, fn)
    ot_path = os.path.join(ot_basepath, fn)
    no_path = os.path.join(no_basepath, fn)
    nt_path = os.path.join(nt_basepath, output_category, fn)

    try:
        ensureDir(nt_path)
    except Exception as e:
        writeExceptionTo(Exception('디렉토리 생성 중 에러: %s' % nt_path, e), log)
        #Directory 생성에 실패했으므로 doFailedCopy는 부르지 않는다
        report_summary[report_case_failed].append(fn)
        return

    try:
        f_oo = filehandler.open(oo_path, False, oo_encoding, oo_autodetect)
        f_ot = filehandler.open(ot_path, False, ot_encoding, ot_autodetect)
        f_no = filehandler.open(no_path, False, no_encoding, no_autodetect)
        f_nt = filehandler.open(nt_path, True, nt_encoding, nt_autodetect)
    except Exception as e:
        writeExceptionTo(Exception('파일을 여는 중 에러 (권한 문제인지 확인하세요)', e), log)
        doFailedCopy(fn, no_basepath, nt_basepath, config['Failed_Out'])
        report_summary[report_case_failed].append(fn)
        return

    try:
        changed = translate.updateFile(f_oo, f_ot, f_no, f_nt, riw=riw, trim_prefix=config['Trim_Prefix'], force_hash=force_hash)
        report_summary[{True: report_case, False: report_case_stay}[changed]].append(fn)
    except Exception as e:
        f_nt.close()
        os.remove(nt_path)
        writeExceptionTo(e, log)
        doFailedCopy(fn, no_basepath, nt_basepath, config['Failed_Out'])
        report_summary[report_case_failed].append(fn)

def update_hash_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    return update_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary, True)

def copy_oo_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    src_info = config['OO_Directory'], config['OO_Encoding'], config['OO_Autodetect']
    dst_info = config['NT_Directory'], config['NT_Encoding'], config['NT_Autodetect']
    copy_handler(config, fn, src_info, dst_info, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary)

def copy_ot_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    src_info = config['OT_Directory'], config['OT_Encoding'], config['OT_Autodetect']
    dst_info = config['NT_Directory'], config['NT_Encoding'], config['NT_Autodetect']
    copy_handler(config, fn, src_info, dst_info, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary)

def copy_no_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    src_info = config['NO_Directory'], config['NO_Encoding'], config['NO_Autodetect']
    dst_info = config['NT_Directory'], config['NT_Encoding'], config['NT_Autodetect']
    copy_handler(config, fn, src_info, dst_info, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary)

def ignore_handler(config, fn, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    log(u'무시합니다.')
    pass

actionList = collections.OrderedDict([
    ('update'        , FileActionItem(update_handler, u'업데이트',)),
    ('update-hash'   , FileActionItem(update_hash_handler, u'업데이트(Hash 번역만 사용)',)),
    ('copy-oo'       , FileActionItem(copy_oo_handler, u'구버전 원본 복사')),
    ('copy-ot'       , FileActionItem(copy_ot_handler, u'구버전 번역본 복사')),
    ('copy-no'       , FileActionItem(copy_no_handler, u'신버전 원본 복사')),
    (''              , FileActionItem(ignore_handler, u'무시')),
])

def doFailedCopy(fn, src_basepath, dst_basepath, dst_category):
    '''fallback용. 그냥 파일 복사만 시도.'''
    '''Exception은 내뱉지 말것'''
    log(u'<실패> 단순복사를 시도합니다.')
    
    src_path = os.path.join(src_basepath, fn)
    dst_path = os.path.join(dst_basepath, dst_category, fn)

    try:
        ensureDir(dst_path)
        shutil.copy(src_path, dst_path)
    except Exception as e:
        log('파일 복사 중 에러: %s -> %s' % (src_path, dst_path))
        log(e)

def copy_handler(config, fn, src_info, dst_info, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    '''파일복사. RI 있으면 시도, 인코딩 변경.'''
    src_basepath, src_encoding, src_autodetect = src_info
    dst_basepath, dst_encoding, dst_autodetect = dst_info

    src_path = os.path.join(src_basepath, fn)
    dst_path = os.path.join(dst_basepath, output_category, fn)

    try:
        ensureDir(dst_path)
    except Exception as e:
        writeExceptionTo(Exception('디렉토리 생성 중 에러: %s' % nt_path, e), log)
        #Directory 생성에 실패했으므로 doFailedCopy는 부르지 않는다
        report_summary[report_case_failed].append(fn)
        return

    try:
        f_src = filehandler.open(src_path, False, src_encoding, src_autodetect)
        f_dst = filehandler.open(dst_path, True, dst_encoding, dst_autodetect)
    except Exception as e:
        writeExceptionTo(Exception('파일을 여는 중 에러 (권한 문제인지 확인하세요)', e), log)
        doFailedCopy(fn, no_basepath, nt_basepath, config['Failed_Out'])
        report_summary[report_case_failed].append(fn)
        return
    
    try:
        translate.copyFile(f_src, f_dst, riw=riw, trim_prefix=config['Trim_Prefix'])
        report_summary[report_case].append(fn)
    except Exception as e:
        f_dst.close()
        os.remove(dst_path)
        writeExceptionTo(e, log)
        doFailedCopy(fn, src_basepath, dst_basepath, config['Failed_Out'])
        report_summary[report_case_failed].append(fn)

####################
#Main functions
####################

#Determine action and redirect
def handleFile(config, fn, file_exist, riw, report_summary):
    current_action = actionList[''] #.handler()

    exist_oo, exist_ot, exist_no = file_exist

    output_fail = config['Failed_Out']
    report_case_stay = ''

    if (exist_oo) and (exist_ot) and (exist_no):
        #case 1: All exist (update)
        #update oo, ot, no (+ri)
        current_action = actionList[config['Case1_Action']]
        output_category = config['Case1_Out']
        do_ri = config['Case1_RI']
        report_case = 'case1'
        report_case_stay = 'case1_stay'
        report_case_failed = 'case1_fail'
            
    elif (exist_oo) and (exist_ot) and (not exist_no):
        #case 2: Deleted in newer version
        #copy ot (+ri)
        current_action = actionList[config['Case2_Action']]
        output_category = config['Case2_Out']
        do_ri = config['Case2_RI']
        report_case = 'case2'
        report_case_failed = 'case2_fail'

    elif (exist_oo) and (not exist_ot) and (exist_no):
        #case 3: Not translated
        #copy no (+ri)
        current_action = actionList[config['Case3_Action']]
        output_category = config['Case3_Out']
        do_ri = config['Case3_RI']
        report_case = 'case3'
        report_case_failed = 'case3_fail'

    elif (exist_oo) and (not exist_ot) and (not exist_no):
        #case 4: Not translated & deleted
        #copy oo (+ri)
        current_action = actionList[config['Case4_Action']]
        output_category = config['Case4_Out']
        do_ri = config['Case4_RI']
        report_case = 'case4'
        report_case_failed = 'case4_fail'

    elif (not exist_oo) and (exist_ot) and (exist_no):
        #case 5: RARE CASE - original in translated version & commited to updated version?!
        #본가에 마수를 끼치는 시대가 오면 가능한 케이스겠지
        #copy no (+ri)
        current_action = actionList[config['Case5_Action']]
        output_category = config['Case5_Out']
        do_ri = config['Case5_RI']
        report_case = 'case5'
        report_case_failed = 'case5_fail'
        
    elif (not exist_oo) and (exist_ot) and (not exist_no):
        #case 6: Original in translation
        #copy ot (+ri)
        current_action = actionList[config['Case6_Action']]
        output_category = config['Case6_Out']
        do_ri = config['Case6_RI']
        report_case = 'case6'
        report_case_failed = 'case6_fail'
            
    elif (not exist_oo) and (not exist_ot) and (exist_no):
        #case 7: New file
        #copy no (+ri)
        current_action = actionList[config['Case7_Action']]
        output_category = config['Case7_Out']
        do_ri = config['Case7_RI']
        report_case = 'case7'
        report_case_failed = 'case7_fail'

    current_action.handler(config, fn, output_category, {True: riw, False: None}[do_ri], report_case, report_case_failed, report_case_stay, report_summary)

#Main function
def batchwork(config):
    """
    return exitcode
    """

    #Phase 1: 디렉토리 구조 읽기

    log(u'디렉토리 구조를 읽는 중입니다...')

    def generateFileList(config):
        filelist_oo = dirFileList(config['OO_Directory'])
        filelist_ot = dirFileList(config['OT_Directory'])
        filelist_no = dirFileList(config['NO_Directory'])
        
        #NT는 없을경우 새로 생성
        ensureDir(os.path.join(config['NT_Directory'], '.'))

        filelist_nt = set()
        #NT의 "하위" 디렉토리의 내용을 취합
        for dirname in os.listdir(config['NT_Directory']):
            dirpath = os.path.join(config['NT_Directory'], dirname)
            filelist_nt.update(dirFileList(dirpath))
        return filelist_oo, filelist_ot, filelist_no ,filelist_nt
    try:
        filelist_oo, filelist_ot, filelist_no ,filelist_nt = generateFileList(config)
    except Exception as e:
        log(u'디렉토리를 읽어올 수 없습니다. 디렉토리가 있는지 확인해주세요.')
        writeExceptionTo(e, log)
        return -1

    #Phase 2: Global Worker 생성

    #ReplaceIndexWorker
    riw = None

    ri_file = config['RI_File']
    if ri_file != u'':
        
        log(u'치환정보를 읽는 중입니다...')

        try:
            f_ri = filehandler.open(ri_file, False, config['RI_Encoding'], config['RI_Autodetect'])
        except Exception as e:
            log(u'%s를 열 수 없습니다. 파일이 있는지 확인해주세요.' % ri_file)
            writeExceptionTo(e, log)
            return -1

        try:
            riw = replaceindex.buildReplaceIndexWorker(f_ri, config['RI_Encoding'], config['RI_Autodetect'])
        except Exception as e:
            log(u'%s를 읽는 중 에러가 발생했습니다.' % ri_file)
            writeExceptionTo(e, log)
            return -1

    #Phase 3: 리포트 초기화

    log(u'리포트를 초기화합니다...')

    try:
        f_report = filehandler.open(config['Report_File'], True, 'utf-8-sig', 'no')
    except Exception as e:
        log(u'%s를 생성하는 중 에러가 발생했습니다.' % config['Report_File'])
        writeExceptionTo(e, log)
        return -1

    def writeToReport(msg):
        f_report.write(u'%s\n' % msg)

    class ReportSummaryItem(list):
        def __init__(self, summaryheader, applyRI, action, *args):
            list.__init__(self, args)
            self.summaryheader = summaryheader
            self.applyRI = applyRI
            self.action = action
    
    report_summary = collections.OrderedDict([
        ('case1_stay'   ,   ReportSummaryItem(u'[%s] 다음 파일들은 변경점이 없습니다. (Case 1)' % config['Case1_Out'], config['Case1_RI'], config['Case1_Action'])),
        ('case1'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 변경점이 있습니다. (Case 1)' % config['Case1_Out'], config['Case1_RI'], config['Case1_Action'])),
        ('case2'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 신버전에서 삭제되었습니다. (Case 2)' % config['Case2_Out'], config['Case2_RI'], config['Case2_Action'])),
        ('case3'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 번역이 되지 않았습니다. (Case 3)' % config['Case3_Out'], config['Case3_RI'], config['Case3_Action'])),
        ('case4'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 신버전에서 삭제되었습니다. 또한 번역도 없습니다. (Case 4)' % config['Case4_Out'], config['Case4_RI'], config['Case4_Action'])),
        ('case5'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 구버전 원본에만 없습니다. (Case 5)' % config['Case5_Out'], config['Case5_RI'], config['Case5_Action'])),
        ('case6'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 구버전 번역본에만 있습니다. (Case 6)' % config['Case6_Out'], config['Case6_RI'], config['Case6_Action'])),
        ('case7'        ,   ReportSummaryItem(u'[%s] 다음 파일들은 신버전에서 새로 생겼습니다. (Case 7)' % config['Case7_Out'], config['Case7_RI'], config['Case7_Action'])),

        ('case1_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 1>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case2_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 2>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case3_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 3>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case4_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 4>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case5_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 5>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case6_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 6>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
        ('case7_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 7>> **실패** 다음 파일은 업데이트 중 에러가 났습니다.' % config['Failed_Out'], False, '')),
    ])

    #Phase 4: 번역

    log(u'번역을 시작합니다...')

    #작업목록: (oo U ot U no) - nt
    filelist_all = (filelist_oo | filelist_ot | filelist_no) - filelist_nt

    #화면 진행상황 표시용

    count_total = len(filelist_all)
    count_current = 0

    for fn in filelist_all:
        with log.logto(writeToReport):

            log(u'[ %s ]' % fn)

            exist_oo = fn in filelist_oo
            exist_ot = fn in filelist_ot
            exist_no = fn in filelist_no

            handleFile(config, fn, (exist_oo, exist_ot, exist_no), riw, report_summary)

            writeToReport(u'')
            f_report.flush() #TODO: 최종판에서 지울것?
            
        
        count_current += 1
        if count_current % 10 == 0 or count_current == count_total:
            log(u'== [%d/%d] 완료' % (count_current, count_total))

    #Phase 5: Summary

    with log.logto(writeToReport):
        
        log(
u'''

########################################################################
########################################################################

                          작업이 완료되었습니다.

########################################################################
########################################################################

''')
        for case in report_summary:
            rsi = report_summary[case]

            if len(rsi) == 0:
                continue

            log(rsi.summaryheader)
            if rsi.action != '':
                log(u'작업: %s' % actionList[rsi.action].description)
            if riw != None:
                log({True: u'(치환이 적용되었습니다)', False: u'(치환은 적용되지 않습니다)'}[rsi.applyRI])
            for i in sorted(rsi):
                log(u' - %s' % i)
            log(u'')
    
    log(u'작업 완료. %s에 리포트가 작성되었습니다.' % config['Report_File'])

    return 0

