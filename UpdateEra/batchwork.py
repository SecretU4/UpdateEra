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
        raise IOError(u'%s ���丮�� �������� �ʽ��ϴ�.' % rootname)
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
    ''' �ڵ������� �� �� �ִ°� '''
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
        writeExceptionTo(Exception('���丮 ���� �� ����: %s' % nt_path, e), log)
        #Directory ������ ���������Ƿ� doFailedCopy�� �θ��� �ʴ´�
        report_summary[report_case_failed].append(fn)
        return

    try:
        f_oo = filehandler.open(oo_path, False, oo_encoding, oo_autodetect)
        f_ot = filehandler.open(ot_path, False, ot_encoding, ot_autodetect)
        f_no = filehandler.open(no_path, False, no_encoding, no_autodetect)
        f_nt = filehandler.open(nt_path, True, nt_encoding, nt_autodetect)
    except Exception as e:
        writeExceptionTo(Exception('������ ���� �� ���� (���� �������� Ȯ���ϼ���)', e), log)
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
    log(u'�����մϴ�.')
    pass

actionList = collections.OrderedDict([
    ('update'        , FileActionItem(update_handler, u'������Ʈ',)),
    ('update-hash'   , FileActionItem(update_hash_handler, u'������Ʈ(Hash ������ ���)',)),
    ('copy-oo'       , FileActionItem(copy_oo_handler, u'������ ���� ����')),
    ('copy-ot'       , FileActionItem(copy_ot_handler, u'������ ������ ����')),
    ('copy-no'       , FileActionItem(copy_no_handler, u'�Ź��� ���� ����')),
    (''              , FileActionItem(ignore_handler, u'����')),
])

def doFailedCopy(fn, src_basepath, dst_basepath, dst_category):
    '''fallback��. �׳� ���� ���縸 �õ�.'''
    '''Exception�� ������ ����'''
    log(u'<����> �ܼ����縦 �õ��մϴ�.')
    
    src_path = os.path.join(src_basepath, fn)
    dst_path = os.path.join(dst_basepath, dst_category, fn)

    try:
        ensureDir(dst_path)
        shutil.copy(src_path, dst_path)
    except Exception as e:
        log('���� ���� �� ����: %s -> %s' % (src_path, dst_path))
        log(e)

def copy_handler(config, fn, src_info, dst_info, output_category, riw, report_case, report_case_failed, report_case_stay, report_summary):
    '''���Ϻ���. RI ������ �õ�, ���ڵ� ����.'''
    src_basepath, src_encoding, src_autodetect = src_info
    dst_basepath, dst_encoding, dst_autodetect = dst_info

    src_path = os.path.join(src_basepath, fn)
    dst_path = os.path.join(dst_basepath, output_category, fn)

    try:
        ensureDir(dst_path)
    except Exception as e:
        writeExceptionTo(Exception('���丮 ���� �� ����: %s' % nt_path, e), log)
        #Directory ������ ���������Ƿ� doFailedCopy�� �θ��� �ʴ´�
        report_summary[report_case_failed].append(fn)
        return

    try:
        f_src = filehandler.open(src_path, False, src_encoding, src_autodetect)
        f_dst = filehandler.open(dst_path, True, dst_encoding, dst_autodetect)
    except Exception as e:
        writeExceptionTo(Exception('������ ���� �� ���� (���� �������� Ȯ���ϼ���)', e), log)
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
        #������ ������ ��ġ�� �ô밡 ���� ������ ���̽�����
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

    #Phase 1: ���丮 ���� �б�

    log(u'���丮 ������ �д� ���Դϴ�...')

    def generateFileList(config):
        filelist_oo = dirFileList(config['OO_Directory'])
        filelist_ot = dirFileList(config['OT_Directory'])
        filelist_no = dirFileList(config['NO_Directory'])
        
        #NT�� ������� ���� ����
        ensureDir(os.path.join(config['NT_Directory'], '.'))

        filelist_nt = set()
        #NT�� "����" ���丮�� ������ ����
        for dirname in os.listdir(config['NT_Directory']):
            dirpath = os.path.join(config['NT_Directory'], dirname)
            filelist_nt.update(dirFileList(dirpath))
        return filelist_oo, filelist_ot, filelist_no ,filelist_nt
    try:
        filelist_oo, filelist_ot, filelist_no ,filelist_nt = generateFileList(config)
    except Exception as e:
        log(u'���丮�� �о�� �� �����ϴ�. ���丮�� �ִ��� Ȯ�����ּ���.')
        writeExceptionTo(e, log)
        return -1

    #Phase 2: Global Worker ����

    #ReplaceIndexWorker
    riw = None

    ri_file = config['RI_File']
    if ri_file != u'':
        
        log(u'ġȯ������ �д� ���Դϴ�...')

        try:
            f_ri = filehandler.open(ri_file, False, config['RI_Encoding'], config['RI_Autodetect'])
        except Exception as e:
            log(u'%s�� �� �� �����ϴ�. ������ �ִ��� Ȯ�����ּ���.' % ri_file)
            writeExceptionTo(e, log)
            return -1

        try:
            riw = replaceindex.buildReplaceIndexWorker(f_ri, config['RI_Encoding'], config['RI_Autodetect'])
        except Exception as e:
            log(u'%s�� �д� �� ������ �߻��߽��ϴ�.' % ri_file)
            writeExceptionTo(e, log)
            return -1

    #Phase 3: ����Ʈ �ʱ�ȭ

    log(u'����Ʈ�� �ʱ�ȭ�մϴ�...')

    try:
        f_report = filehandler.open(config['Report_File'], True, 'utf-8-sig', 'no')
    except Exception as e:
        log(u'%s�� �����ϴ� �� ������ �߻��߽��ϴ�.' % config['Report_File'])
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
        ('case1_stay'   ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� �������� �����ϴ�. (Case 1)' % config['Case1_Out'], config['Case1_RI'], config['Case1_Action'])),
        ('case1'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� �������� �ֽ��ϴ�. (Case 1)' % config['Case1_Out'], config['Case1_RI'], config['Case1_Action'])),
        ('case2'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� �Ź������� �����Ǿ����ϴ�. (Case 2)' % config['Case2_Out'], config['Case2_RI'], config['Case2_Action'])),
        ('case3'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� ������ ���� �ʾҽ��ϴ�. (Case 3)' % config['Case3_Out'], config['Case3_RI'], config['Case3_Action'])),
        ('case4'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� �Ź������� �����Ǿ����ϴ�. ���� ������ �����ϴ�. (Case 4)' % config['Case4_Out'], config['Case4_RI'], config['Case4_Action'])),
        ('case5'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� ������ �������� �����ϴ�. (Case 5)' % config['Case5_Out'], config['Case5_RI'], config['Case5_Action'])),
        ('case6'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� ������ ���������� �ֽ��ϴ�. (Case 6)' % config['Case6_Out'], config['Case6_RI'], config['Case6_Action'])),
        ('case7'        ,   ReportSummaryItem(u'[%s] ���� ���ϵ��� �Ź������� ���� ������ϴ�. (Case 7)' % config['Case7_Out'], config['Case7_RI'], config['Case7_Action'])),

        ('case1_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 1>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case2_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 2>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case3_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 3>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case4_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 4>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case5_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 5>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case6_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 6>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
        ('case7_fail'   ,   ReportSummaryItem(u'[%s] <<ERROR @ Case 7>> **����** ���� ������ ������Ʈ �� ������ �����ϴ�.' % config['Failed_Out'], False, '')),
    ])

    #Phase 4: ����

    log(u'������ �����մϴ�...')

    #�۾����: (oo U ot U no) - nt
    filelist_all = (filelist_oo | filelist_ot | filelist_no) - filelist_nt

    #ȭ�� �����Ȳ ǥ�ÿ�

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
            f_report.flush() #TODO: �����ǿ��� �����?
            
        
        count_current += 1
        if count_current % 10 == 0 or count_current == count_total:
            log(u'== [%d/%d] �Ϸ�' % (count_current, count_total))

    #Phase 5: Summary

    with log.logto(writeToReport):
        
        log(
u'''

########################################################################
########################################################################

                          �۾��� �Ϸ�Ǿ����ϴ�.

########################################################################
########################################################################

''')
        for case in report_summary:
            rsi = report_summary[case]

            if len(rsi) == 0:
                continue

            log(rsi.summaryheader)
            if rsi.action != '':
                log(u'�۾�: %s' % actionList[rsi.action].description)
            if riw != None:
                log({True: u'(ġȯ�� ����Ǿ����ϴ�)', False: u'(ġȯ�� ������� �ʽ��ϴ�)'}[rsi.applyRI])
            for i in sorted(rsi):
                log(u' - %s' % i)
            log(u'')
    
    log(u'�۾� �Ϸ�. %s�� ����Ʈ�� �ۼ��Ǿ����ϴ�.' % config['Report_File'])

    return 0

