'''
Created on 30 Aug 2013

@author: habisain
'''

import multiprocessing
from errorhook import ErrorClass

class Patcher(ErrorClass):
    def __init__(self, jobs, translator, comsout):
        self.jobs = jobs
        self.translator = translator
        self.comsout = comsout
        self.rets = {}
        self.progress = 0
        self.pool = None
        
    def start(self):
        if self.pool is not None:
            raise Exception('Tried to start patcher multiple times')
        self.pool = multiprocessing.pool()
        for jobName, jobFunc, jobArgs in self.jobs:
            self.rets[jobName] = self.pool.apply_async(jobFunc, jobArgs)
        
    def finishJob(self):
        self.progress += 1
        self.comsout.setProgress('patching', self.progress / len(self.jobs))