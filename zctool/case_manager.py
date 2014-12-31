#!/usr/bin/python
import logging
from test_result_enum import *

class CaseManager(object):
    def __init__(self, callback_function):
        self.callback_function = callback_function
        self.enviro = {}
        self.case_list = []
        self.offset = 0
        self.test_result = None

    def getFirstCase(self):
        return self.case_list[0]

    def hasMoreCase(self):
        return ((self.offset + 1) < len(self.case_list))
    
    def getNextCase(self):
        self.offset += 1
        if self.offset != len(self.case_list):
            return self.case_list[self.offset]
        else:
            return None

    def addTestCase(self, case):
        self.case_list.append(case)

    def clearTestCase(self):
        while len(self.case_list):
            self.case_list.remove(self.case_list[0])
        self.offset = 0
        
    def finishTestCase(self, result):
        name = self.case_list[self.offset].name
        self.callback_function(name, result)
        self.test_result = result
        self.clearTestCase()

    def getParam(self):
        return self.enviro
