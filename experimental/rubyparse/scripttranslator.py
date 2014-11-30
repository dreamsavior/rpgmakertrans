'''
scripttranslator
****************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Provides the functionality to handle the various succession rules.
'''

class ScriptTranslator:
    def __init__(self, string, translationHandler):
        self.string = string
        self.output = None
        self.translationIndices = []
        self.translationHandler = translationHandler
        
    def addIndicies(self, indicies):
        self.translationIndices.append(indicies)
        
    def rollback(self, index):
        self.translationIndices = [indices for indices in self.translationIndices if indices[0] < index]
        
    def translate(self):
        for indicies in self.translationIndices:
            self.translationHandler.translate(self.string[indicies[0]:indicies[1]])