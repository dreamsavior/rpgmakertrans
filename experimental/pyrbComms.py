"""
pyrbComms
*********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

Experimental Python/Ruby communications. Ideally, would like this to happen
over STDIN/STDOUT rather than file based as present. 

"""

import ast

def stringify(string):
    sLiteral = isinstance(string, str)
    string = str(string)
    string = string.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"') #encode('string_escape')
    if sLiteral:
        return '"' +  string + '"'
    else:
        return string
    
def loadFromString(string):
    return ast.literal_eval(string)
    
def loadFromFile(fn):
    with open(fn, 'rb') as f:
        string = f.read()
    return loadFromString(string)
    
def dumpTranslations(transDict):
    data = ['{']
    for key in transDict:
        val = transDict[key]
        data.append(stringify(key))
        data.append('=>{')
        data2 = []
        for key2 in val:
            val2 = val[key2]
            data2.append(stringify(key2) + '=>' + stringify(val2))
        data.append(', '.join(data2))
        data.append('}, ')
    data += ['}']
    return ''.join(data)

def dumpTranslationsToFile(transDict, fn):
    with open(fn, 'wb') as f:
        f.write(dumpTranslations(transDict))

if __name__ == '__main__':
    translations, transOrder = loadFromFile('CommonEvents.pyf')
    dumpTranslationsToFile(translations, 'CommonEvents.rbf')
