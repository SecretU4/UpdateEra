#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ['writeExceptionTo', 'log', 'LRU']




def writeExceptionTo(e, printfunc):
    printfunc(u'\t(에러 내용): ')
    for i in e.args:
        printfunc(u'\t%s' % unicode(i))

class __Log(object):
    def __init__(self):
        self.logstack = []
        self.logfunc = lambda x: None

    class LogStack(object):
        def __init__(self, log, logfunc):
            self.log = log
            self.logfunc = logfunc

        def __enter__(self):
            self.log.logstack.append(self.log.logfunc)
            self.log.logfunc = self.logfunc

        def __exit__(self, type, value, traceback):
            self.log.logfunc = self.log.logstack.pop()

    def logto(self, logfunc):
        return self.LogStack(self, logfunc)

    def __call__(self, msg):
        return self.logfunc(msg)

log = __Log()




class Node(object):
    __slots__ = ['prev', 'next', 'me']
    def __init__(self, prev, me):
        self.prev = prev
        self.me = me
        self.next = None

class LRU:
    def __init__(self, count, pairs=[]):
        self.count = max(count, 1)
        self.d = {}
        self.first = None
        self.last = None
        for key, value in pairs:
            self[key] = value
    
    def __contains__(self, obj):
        return obj in self.d

    def __getitem__(self, obj):
        a = self.d[obj].me
        self[a[0]] = a[1]
        return a[1]

    def __setitem__(self, obj, val):
        if obj in self.d:
            del self[obj]
        nobj = Node(self.last, (obj, val))
        if self.first is None:
            self.first = nobj
        if self.last:
            self.last.next = nobj
        self.last = nobj
        self.d[obj] = nobj
        if len(self.d) > self.count:
            if self.first == self.last:
                self.first = None
                self.last = None
                return
            a = self.first
            a.next.prev = None
            self.first = a.next
            a.next = None
            del self.d[a.me[0]]
            del a

    def __delitem__(self, obj):
        nobj = self.d[obj]
        if nobj.prev:
            nobj.prev.next = nobj.next
        else:
            self.first = nobj.next
        if nobj.next:
            nobj.next.prev = nobj.prev
        else:
            self.last = nobj.prev
        del self.d[obj]

    def __iter__(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me[1]
            cur = cur2

    def iteritems(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me
            cur = cur2

    def iterkeys(self):
        return iter(self.d)

    def itervalues(self):
        for i,j in self.iteritems():
            yield j

    def keys(self):
        return self.d.keys()
