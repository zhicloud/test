#!/usr/bin/python

class MessageCacheTask(object):
    max_timeout = 10
    def __init__(self):
        self.finished = False
        self.total = 0
        self.timeout = 0
        ##key=index, value = content
        self.cache = {}

    def initial(self, index, total, data):
        self.total = total
        self.cache[index] = data
        self.finished = False

    def add(self, index, data):
        self.cache[index] = data
        if len(self.cache) == self.total:
            ##finished
            self.finished = True

    def obtain(self):
        result = ""
        for i in range(self.total):
            index = i + 1
            result += self.cache[index]
            
        return result

    def checkTimeout(self):
        self.timeout += 1
        if self.timeout > self.max_timeout:
            ##timeout
            return True
        else:
            return False
