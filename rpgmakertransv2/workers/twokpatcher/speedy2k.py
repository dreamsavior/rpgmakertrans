"""
speedy2k
********

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2014
:license: GNU Public License version 3

The second version of the 2k patching engine, which has the property
of being much faster than the first version.

TODO: Investigate using either ctypes or cffi instead of struct/unpack.
These may be nicer in terms of performance/layout.
"""

from struct import unpack, Struct
from .speedy2kconstants import schemas, containerTypes
from ...errorhook import ErrorClass

class BytesOrNoneList(list):

    def append(self, item):
        if isinstance(item, bytes) or item is None:
            return super().append(item)
        else:
            raise Exception('Appended something dodgy')

    def extend(self, ls):
        for x in ls:
            self.append(x)


class RPGFile(ErrorClass):

    def __init__(self, name, string, schemas, translator, *args, **kwargs):
        super(RPGFile, self).__init__(*args, **kwargs)
        self.name = name
        self.string = string
        self.intstring = unpack('B' * len(string), self.string)
        self.index = 0
        self.output = BytesOrNoneList()  # []
        self.translator = translator

        self.schemaToFunc = {
            'script': self.parseScript,
            'blocks': self.parseBlocks,
            'stringData': self.parseStrings}
        global containerTypes
        for containerType in containerTypes:
            self.schemaToFunc[containerType] = self.parseContainer
        self.schemas = schemas
        self.packers = {}
        self.contextToTranslator = {
            'Message': self.translateMessage,
            'Choice': self.translateChoice,
            'SetStringVars': self.translateStringData,
            'ChoiceStarter': self.translateChoiceStarter}

    def translate(self, string, context):
        """Wrapper function to convert old calls into new global translator calls"""
        retries = 100
        r = None
        while r is None and retries != 0:
            try:
                r = self.translator.translate(string, (self.name, context))
            except TypeError:
                retries -= 1
        if r is None:
            # TODO: Nonfatal error
            r = string
        return r

    def outputfile(self, fn):
        with open(fn, 'wb') as f:
            f.write(b''.join(self.output))

    def getPacker(self, n):
        if n not in self.packers:
            self.packers[n] = Struct('B' * n)
        return self.packers[n]

    def rpgintw(self, n):
        result = []
        result.append(n & 127)
        n = n >> 7
        while n:
            result.append((n & 127) | 128)
            n = n >> 7
        result.reverse()
        return [self.getPacker(len(result)).pack(*result)]

    def rpgintsw(self, ints):
        result = []
        for n in [len(ints)] + ints:
            partResult = []
            partResult.append(n & 127)
            n = n >> 7
            while n:
                partResult.append((n & 127) | 128)
                n = n >> 7
            partResult.reverse()
            result.extend(partResult)
        return [self.getPacker(len(result)).pack(*result)]

    def matchString(self, newstring):
        # returns True and moves on if string matches
        # else returns False (and doesn't move on)
        if self.string.startswith(newstring, self.index):
            self.index += len(newstring)
            self.output.append(newstring)
            return True
        else:
            return False

    def rpgint(self):
        # returns: rpgint from current position
        done = False
        result = 0
        while not done:
            result = result << 7
            newint = self.intstring[self.index]
            self.index += 1
            if not newint & 128:
                done = True
            result += newint & 127
        return result

    def bytesrw(self):
        # returns only the indices of a bytes thing, for later copying
        start = self.index
        length = self.rpgint()
        self.index += length
        self.output.append(self.string[start:self.index])
        # if '.png' in self.output[-1]:
        #    print 'FOUND IMAGE'

    def blindbytes(self):
        # advances by a bytes object, returning nothing
        length = self.rpgint()
        self.index += length

    def blindrpgints(self):
        # reads an rpgint, then advances by that many rpgints, returning
        # nothings
        n = self.rpgint()
        while n:
            newint = self.intstring[self.index]
            self.index += 1
            if not newint & 128:
                n -= 1

    def blindrpgintsrw(self):
        start = self.index
        n = self.rpgint()
        while n:
            newint = self.intstring[self.index]
            self.index += 1
            if not newint & 128:
                n -= 1
        self.output.append(self.string[start:self.index])

    def rpgints(self):
        # read an rpgint, return it and return that many following rpgints
        n = self.rpgint()
        ret = []
        newint = 0
        while n:
            newint = (newint << 7) + self.intstring[self.index] & 127
            self.index += 1
            if not newint & 128:
                n -= 1
                ret.append(newint)
                newint = 0
        return ret

    def rpgintsAsRaw(self):
        # reads an rpgint, and then returns it and that many rpgints in raw
        # form
        start = self.index
        n = self.rpgint()
        while n:
            newint = self.intstring[self.index]
            self.index += 1
            if not newint & 128:
                n -= 1
        return self.string[start:self.index]

    def bytes(self):
        # returns: bytes from current position
        # Assumes bytes are prefixed with an rpgint length
        length = self.rpgint()
        ret = self.string[self.index:self.index + length]
        self.index += length
        return ret

    def bytesw(self, bytes):
        self.output.extend(self.rpgintw(len(bytes)))
        self.output.append(bytes)

    def parseStrings(self, schema, currentLen, contextInfo=0):
        defaultStrings = schema['defaultStringData']
        cntAttribID = self.rpgint()
        while cntAttribID and self.index < currentLen:
            self.output.extend(self.rpgintw(cntAttribID))
            string = self.bytes()
            transString = self.translate(string,
                'stringData/' + defaultStrings[cntAttribID])
            self.bytesw(transString)
            cntAttribID = self.rpgint()
        self.output.append(b'\x00')

    def parseContainer(self, schema, currentLen, contextInfo=0):
        cntNoOfItems = self.rpgint()
        scriptLenPos = None
        self.output.extend(self.rpgintw(cntNoOfItems))
        while cntNoOfItems and self.index < currentLen:
            cntItemID = self.rpgint()
            self.output.extend(self.rpgintw(cntItemID))
            cntAttribID = self.rpgint()
            self.output.extend(self.rpgintw(cntAttribID))
            while cntAttribID != 0 and self.index < currentLen:
                if cntAttribID in schema:
                    newSchemaType, newSchemaDict = schema[cntAttribID]
                    end = 0
                    if newSchemaType == 'string':
                        string = self.bytes()
                        contextData = (contextInfo, cntAttribID, cntItemID)
                        transString = self.translate(string, contextData)
                        self.bytesw(transString)

                    elif newSchemaType == 'bytes':
                        self.bytesrw()
                    elif newSchemaType == 'scriptLength':
                        length = self.bytes()
                        scriptLenPos = len(self.output)
                        self.output.append(None)
                    elif newSchemaType == 'script':
                        length = self.rpgint()
                        end = self.index + length
                        self.output.append(None)
                        startIndex = len(self.output)
                        self.parseScript(newSchemaDict, end)
                        length = sum(
                            (len(
                                self.output[x]) for x in range(
                                startIndex, len(
                                    self.output))))
                        lengthRaw = b''.join(self.rpgintw(length))
                        self.output[startIndex - 1] = lengthRaw
                        if scriptLenPos is not None:
                            self.output[scriptLenPos] = b''.join(
                                self.rpgintw(
                                    len(lengthRaw))) + lengthRaw
                            scriptLenPos = None
                        else:
                            raise Exception(
                                'Script without preceding script length')
                        if self.index != end:
                            print('weirdness', newSchemaType)
                    elif newSchemaType in self.schemaToFunc:
                        length = self.rpgint()
                        end = self.index + length
                        self.output.append(None)
                        startIndex = len(self.output)
                        self.schemaToFunc[newSchemaType](newSchemaDict, end)
                        length = sum(
                            (len(
                                self.output[x]) for x in range(
                                startIndex, len(
                                    self.output))))
                        self.output[
                            startIndex -
                            1] = b''.join(
                            self.rpgintw(length))
                        if self.index != end:
                            print('weirdness', newSchemaType)
                    else:
                        raise Exception('Dunno what to do')
                else:
                    # assume its uninteresting
                    self.bytesrw()
                cntAttribID = self.rpgint()
                self.output.extend(self.rpgintw(cntAttribID))

            cntNoOfItems -= 1

    def translateMessage(self, cmdList, schema, depth, translator,
                        collStart, collEnd):
        text = b'\n'.join((x[2] for x in cmdList))

        transText = self.translate(text, 'Dialogue/Message/FaceUnknown')
        if transText != text:
            x = 0
            message, messageNextLine = schema[
                'message'], schema['messageNextLine']
            for line in transText.split(b'\n'):
                opcode = message if x == 0 else messageNextLine
                x = (x + 1) % 4
                self.output.extend(self.rpgintw(opcode))
                self.output.extend(self.rpgintw(depth))
                self.output.extend(self.rpgintw(len(line)))
                self.output.append(line)
                self.output.append(b'\x00')
        else:
            self.output.append(self.string[collStart:collEnd])

    def translateChoice(self, cmdList, schema, depth, translator,
                        collStart, collEnd):
        cmd = cmdList[0]
        transText = self.translate(cmd[2], 'Dialogue/Choice')
        if transText != cmd[2]:
            choiceCode = schema['nextChoice']
            args = cmd[1]
            line = transText
            self.output.extend(self.rpgintw(choiceCode))
            self.output.extend(self.rpgintw(depth))
            self.output.extend(self.rpgintw(len(line)))
            self.output.append(line)
            self.output.extend(self.rpgintsw(args))
        else:
            self.output.append(self.string[collStart:collEnd])

    def translateChoiceStarter(self, cmdList, schema, depth, translator,
                               collStart, collEnd):
        translated = False
        textLS = []
        for opc, args, line in cmdList:
            lineTrans = line
            for part in line.split(b'/'):
                translation = self.translate(part, 'Dialogue/Choice')
                translated |= part != translation
                lineTrans = lineTrans.replace(part, translation)
            textLS.append(lineTrans)
        if translated:
            for x in range(len(cmdList)):
                opc, args, line = cmdList[x]
                lineTrans = textLS[x]
                self.output.extend(self.rpgintw(opc))
                self.output.extend(self.rpgintw(depth))
                self.output.extend(self.rpgintw(len(lineTrans)))
                self.output.append(lineTrans)
                self.output.extend(self.rpgintsw(args))
        else:
            self.output.append(self.string[collStart:collEnd])

    def translateStringData(self, cmdList, schema, depth, translator,
                            collStart, collEnd):
        textLS = []
        changeName, changeClass = schema['changename'], schema['changeclass']
        for opc, args, string in cmdList:
            if opc == changeName:
                textLS.append(b'\\n[')
            elif opc == changeClass:
                textLS.append(b'\\c[')
            else:
                raise Exception('Something bad happened')
            #print(args[0], type(args[0]), bytes(args[0]))
            textLS.append(str(args[0]).encode(encoding='ascii'))
            textLS.append(b']:')
            textLS.append(string)
            textLS.append(b'\n')
        textStr = b''.join(textLS).strip(b'\n')
        transString = self.translate(textStr, 'Dialogue/SetHeroName')
        if transString != textStr:
            for line in transString.split(b'\n'):
                if line.strip():
                    p1, colon, string = line.partition(b':')
                    code, bracket, intPart = p1.partition(b'[')
                    code = code.strip(b'\\')
                    intPart = intPart.strip(b']')
                    args = [int(intPart.decode(encoding='ascii'))]
                    if code == b'c':
                        opcode = changeClass
                    elif code == b'n':
                        opcode = changeName
                    else:
                        raise Exception('A different problem')
                    self.output.extend(self.rpgintw(opcode))
                    self.output.extend(self.rpgintw(depth))
                    self.output.extend(self.rpgintw(len(string)))
                    self.output.append(string)
                    self.output.extend(self.rpgintsw(args))
        else:
            self.output.append(self.string[collStart:collEnd])

    def parseScript(self, schema, currentLen, contextInfo=0):
        scriptList = []
        currentDepth = 0
        scriptError = False
        collecting = False
        currentCollection = []
        currentCollectionType = None
        collStart = 0
        faceOn = False  # Need to work out how to get this variable correctly!
        # Probably on the lines of: if face opcode has a string, it's on, else
        # it's off
        startCollecting = schema['startCollects']
        opcode = -1

        while self.index < currentLen and opcode != 0:
            start = self.index
            opcode = self.rpgint()
            newDepth = self.rpgint()
            if currentCollectionType is not None and (
                    opcode not in collecting or newDepth != currentDepth):
                transFunc = self.contextToTranslator[currentCollectionType]
                transFunc(
                    currentCollection,
                    schema,
                    currentDepth,
                    None,
                    collStart,
                    start)
                currentCollectionType = None
                currentCollection = []

            if currentCollectionType is not None and opcode in collecting:
                stringVar = self.bytes()
                numbers = self.rpgints()
                currentCollection.append((opcode, numbers, stringVar))
            elif opcode in startCollecting:
                stringVar = self.bytes()
                numbers = self.rpgints()
                currentCollection = [(opcode, numbers, stringVar)]
                collecting, currentCollectionType = startCollecting[opcode]
                collStart = start
            else:
                self.output.extend(self.rpgintw(opcode))
                self.output.extend(self.rpgintw(newDepth))
                self.bytesrw()
                self.blindrpgintsrw()

            currentDepth = newDepth

    def parse(self):
        self.index = 0
        matched = False
        for schemaName in self.schemas:
            if self.matchString(schemaName):
                matched = True
                schemaName, schemaDict = self.schemas[schemaName]
                if schemaName in self.schemaToFunc:
                    self.schemaToFunc[schemaName](schemaDict, len(self.string))
                else:
                    Exception('Not sure what to do')
        if not matched:
            raise Exception('Could not parse file: no matching schema')

    def parseBlocks(self, schema, currentLen, contextInfo=0):
        global containerTypes
        retDict = {}
        while self.index < currentLen:
            id = self.rpgint()
            self.output.extend(self.rpgintw(id))  # convert to use raw copy
            if id in schema:
                length = self.rpgint()
                end = self.index + length
                self.output.append(None)
                startIndex = len(self.output)

                newSchemaType, newSchemaDict = schema[id]
                self.schemaToFunc[newSchemaType](newSchemaDict, end, id)
                length = sum(
                    (len(
                        self.output[x]) for x in range(
                        startIndex, len(
                            self.output))))

                self.output[startIndex - 1] = b''.join(self.rpgintw(length))

                if end != self.index:
                    print(hex(id), 'weirdness', newSchemaType)
                self.index = end
            elif id != 0:
                self.bytesrw()


class TwoKRPGFile(RPGFile):

    def __init__(self, name, infn, translator):
        with open(infn, 'rb') as f:
            x = f.read()
        super(TwoKRPGFile, self).__init__(name, x, schemas, translator)


def hexdiff(str, other):
    import binascii
    breaks = 0
    x = 0
    while x < (min(len(str), len(other))) and breaks < 10:
        if str[x] != other[x]:
            breaks += 1
            print('break', breaks, 'pos', x)
            print(binascii.hexlify(str[x - 10:x + 10]))
            print(binascii.hexlify(other[x - 10:x + 10]))
            x += 10
        else:
            x += 1
