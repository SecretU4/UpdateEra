from utility import *
import collections
import io

class Report(object):
    def __init__(self):
        self.entries = collections.OrderedDict()
    def newFile(self, fn, category):
        self.entries[fn] = (category, io.StringIO())
        return log.logto(lambda msg: self.entries[fn][1].write(u'%d\n' % msg))
    def generate(self, generator):
        return generator.generate(self.entries)

class Generator(object):
    def __init__(self, fn):

        pass
    def generate(self, entries):
        pass