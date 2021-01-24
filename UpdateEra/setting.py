#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import codecs
import filehandler
import batchwork

#Exception definition

class SettingEncodeError(Exception):
    pass

class SettingDecodeError(Exception):
    pass

class SettingMissingError(Exception):
    pass



#Automation of setting entries

def __encoding_check(x):
    codecs.lookup(x)
    return str(x)

def __autodetect_check(x):
    if not filehandler.isAvailableAutodetectMode(x):
        raise LookupError(u'unknown autodetect mode: %s' % autodetect)
    return str(x)

class __entry(object):
    def __init__(self, **args):
        self.mandatory = args.get('mandatory', False)
        self.encode = args.get('encode', lambda x: x)
        self.decode = args.get('decode', lambda x: x)
        self.default = args.get('default', None)

class __action_check(object):
    def __init__(self, case):
        self.case = case
    def __call__(self, x):
        if not batchwork.isAvailableAction(self.case, x):
            raise LookupError(u'unknown action mode: %s' % x)
        return str(x)

#####################################################################################################################################
#####################################################################################################################################

__settingEntry = {
    #input dirs
    'OO_Directory': __entry( mandatory=True, encode=unicode, decode=unicode, default='' ),
    'OT_Directory': __entry( mandatory=True, encode=unicode, decode=unicode, default='' ),
    'NO_Directory': __entry( mandatory=True, encode=unicode, decode=unicode, default='' ),
    'NT_Directory': __entry( mandatory=True, encode=unicode, decode=unicode, default='' ),

    'OO_Encoding': __entry( mandatory=False, encode=__encoding_check, decode=__encoding_check, default='utf-8-sig' ),
    'OT_Encoding': __entry( mandatory=False, encode=__encoding_check, decode=__encoding_check, default='utf-8-sig' ),
    'NO_Encoding': __entry( mandatory=False, encode=__encoding_check, decode=__encoding_check, default='utf-8-sig' ),
    'NT_Encoding': __entry( mandatory=False, encode=__encoding_check, decode=__encoding_check, default='utf-8-sig' ),

    'OO_Autodetect': __entry( mandatory=False, encode=__autodetect_check, decode=__autodetect_check, default='no' ),
    'OT_Autodetect': __entry( mandatory=False, encode=__autodetect_check, decode=__autodetect_check, default='no' ),
    'NO_Autodetect': __entry( mandatory=False, encode=__autodetect_check, decode=__autodetect_check, default='no' ),
    'NT_Autodetect': __entry( mandatory=False, encode=__autodetect_check, decode=__autodetect_check, default='no' ),

    #replaceindex file

    'RI_File': __entry( mandatory=False, encode=unicode, decode=unicode, default='' ),
    'RI_Encoding': __entry( mandatory=False, encode=__encoding_check, decode=__encoding_check, default='utf-8-sig' ),
    'RI_Autodetect': __entry( mandatory=False, encode=__autodetect_check, decode=__autodetect_check, default='no' ),

    #output configuration

    'Case1_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'update' ),
    'Case2_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'deleted' ),
    'Case3_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'not_translated' ),
    'Case4_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'deleted' ),
    'Case5_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'rare_case' ),
    'Case6_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'translation_only' ),
    'Case7_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'new' ),
    'Failed_Out': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'failed' ),

    #각 case에 치환을 적용할 것인가?

    'Case1_RI': __entry( mandatory=False, encode=bool, decode=bool, default=True ),
    'Case2_RI': __entry( mandatory=False, encode=bool, decode=bool, default=False ),
    'Case3_RI': __entry( mandatory=False, encode=bool, decode=bool, default=True ),
    'Case4_RI': __entry( mandatory=False, encode=bool, decode=bool, default=False ),
    'Case5_RI': __entry( mandatory=False, encode=bool, decode=bool, default=True ),
    'Case6_RI': __entry( mandatory=False, encode=bool, decode=bool, default=True ),
    'Case7_RI': __entry( mandatory=False, encode=bool, decode=bool, default=True ),

    #각 case별 작업

    'Case1_Action': __entry( mandatory=False, encode=__action_check(1), decode=__action_check(1), default='update' ),
    'Case2_Action': __entry( mandatory=False, encode=__action_check(2), decode=__action_check(2), default='copy-ot' ),
    'Case3_Action': __entry( mandatory=False, encode=__action_check(3), decode=__action_check(3), default='copy-no' ),
    'Case4_Action': __entry( mandatory=False, encode=__action_check(4), decode=__action_check(4), default='copy-oo' ),
    'Case5_Action': __entry( mandatory=False, encode=__action_check(5), decode=__action_check(5), default='copy-no' ),
    'Case6_Action': __entry( mandatory=False, encode=__action_check(6), decode=__action_check(6), default='copy-ot' ),
    'Case7_Action': __entry( mandatory=False, encode=__action_check(7), decode=__action_check(7), default='copy-no' ),

    #리포트 파일 이름
    'Report_File': __entry( mandatory=True, encode=unicode, decode=unicode, default=u'report.txt' ),

    #Hash 번역 강제적용 여부
    'Force_Hash': __entry( mandatory=False, encode=bool, decode=bool, default=False ),

    #Trim을 적용할 prefix character
    'Trim_Prefix': __entry( mandatory=False, encode=unicode, decode=unicode, default=u'' ),
}

#####################################################################################################################################
#####################################################################################################################################

#Main Functions

def saveSetting(fn, setting):
    '''
    fn: filename to save
    setting: dict of 'configname' : 'save' pair
    '''

    final = {}

    for i in __settingEntry:
        if i in setting:
            try:
                final[i] = __settingEntry[i].encode(setting[i])
            except Exception as e:
                raise SettingEncodeError(e)
        else:
            if __settingEntry[i].mandatory:
                raise SettingMissingError('%s가 없습니다.' % i)
            #final[i] = __settingEntry[i].default

    with filehandler.open(fn, True, 'utf-8-sig', 'no') as f:
        json.dump(final, f, indent=4)


def loadSetting(fn):
    '''
    fn: filename of setting file
    '''

    with filehandler.open(fn, False, 'utf-8-sig', 'mskanji') as f:
        setting = json.load(f)

    final = {}
    for i in __settingEntry:
        if i in setting:
            try:
                final[i] = __settingEntry[i].decode(setting[i])
            except Exception as e:
                raise SettingDecodeError(e)
        else:
            if __settingEntry[i].mandatory:
                raise SettingMissingError(u'%s가 없습니다.' % i)
            final[i] = __settingEntry[i].default

    return final
