import random
from ..twokpatcher.speedy2kconstants import contextDict, rtsubsections
from .translatorbase import Translator
from collections import defaultdict
from ...errorhook import ErrorMeta

###########!######! TRANSLATED TEXT #############!###!
shopMenu = '49 char limit'
battleStuff = '49 char limit'
shortLimit = '2 char limt'
charName = '12 char limit'
menuThingName = '19 char limit'
menuItem = '10 char limit'
menuTextLine = '54 char limit'
mainMenuThing = '20 char limit'
statThing = '3 char limit'
attributeName = '8 char limit'
equipThing = '10 char limit'
adviceDict = {}
adviceDict['Dialogue/Message/FaceUnknown'] = '49 char limit (35 if face)'
adviceDict['Dialogue/SetHeroNames'] = charName + ' per name'
adviceDict['Dialogue/Choice'] = '49 char limit'
adviceDict['attributeDataAttr/AttributeName'] = attributeName
adviceDict['conditionDataAttr/ConditionName'] = '8 char limit'
adviceDict['heroAttr/ClassName'] = charName
adviceDict['heroAttr/HeroName'] = charName
adviceDict['heroAttr/MagicName'] = charName
adviceDict['itemAttr/Description'] = menuTextLine
adviceDict['itemAttr/ItemName'] = menuThingName
adviceDict['itemAttr/UsageMessage'] = battleStuff
adviceDict['monsterAttr/MonsterName'] = charName
adviceDict['monsterPartyAttr/MonsterPartyName'] = charName
adviceDict['skillAttr/SkillName'] = menuThingName
adviceDict['skillAttr/Description'] = menuTextLine
adviceDict['skillAttr/UsageText'] = battleStuff
adviceDict['skillAttr/FailureMessage'] = battleStuff
adviceDict['stringData/"normal" status'] = attributeName
adviceDict['stringData/Accessory'] = equipThing
adviceDict['stringData/Agility'] = statThing
adviceDict['stringData/Ally critical hit'] = battleStuff
adviceDict['stringData/Ally damaged'] = battleStuff
adviceDict['stringData/Ally lost via absorb'] = battleStuff
adviceDict['stringData/Ally undamaged'] = battleStuff
adviceDict['stringData/Armor'] = equipThing
adviceDict['stringData/Attack'] = statThing
adviceDict['stringData/Attack dodged'] = battleStuff
adviceDict['stringData/Attack message'] = battleStuff
adviceDict['stringData/Battle defeat'] = battleStuff
adviceDict['stringData/Battle victory'] = battleStuff
adviceDict['stringData/Buy message a'] = shopMenu
adviceDict['stringData/Buy message b'] = shopMenu
adviceDict['stringData/Buy message c'] = shopMenu
adviceDict['stringData/Buying message a'] = shopMenu
adviceDict['stringData/Buying message b'] = shopMenu
adviceDict['stringData/Buying message c'] = shopMenu
adviceDict['stringData/Combat: auto'] = menuItem
adviceDict['stringData/Combat: command'] = menuItem
adviceDict['stringData/Combat: run'] = menuItem
adviceDict['stringData/Command: attack'] = menuItem
adviceDict['stringData/Command: defend'] = menuItem
adviceDict['stringData/Command: item'] = menuItem
adviceDict['stringData/Command: skill'] = menuItem
adviceDict['stringData/Defend message'] = battleStuff
adviceDict['stringData/Defense'] = statThing
adviceDict['stringData/Enemy critical hit'] = battleStuff
adviceDict['stringData/Enemy damaged'] = battleStuff
adviceDict['stringData/Enemy encounter'] = battleStuff
adviceDict['stringData/Enemy escape'] = battleStuff
adviceDict['stringData/Enemy lost via absorb'] = battleStuff
adviceDict['stringData/Enemy transform'] = battleStuff
adviceDict['stringData/Enemy undamaged'] = battleStuff
adviceDict['stringData/Equipped items'] = equipThing
adviceDict['stringData/Escape failure'] = battleStuff
adviceDict['stringData/Escape success'] = battleStuff
adviceDict['stringData/Exit game message'] = menuTextLine
adviceDict['stringData/Exit to windows'] = mainMenuThing
adviceDict['stringData/Experience (short)'] = shortLimit
adviceDict['stringData/Experience received'] = battleStuff
adviceDict['stringData/File name'] = '?'+menuTextLine
adviceDict['stringData/Gathering energy'] = battleStuff
adviceDict['stringData/General yes'] = '4 char limit'
adviceDict['stringData/General no'] = '4 char limit'
adviceDict['stringData/Headstart attack'] = battleStuff
adviceDict['stringData/Health'] = statThing
adviceDict['stringData/Health (short)'] = shortLimit
adviceDict['stringData/Helmet'] = equipThing
adviceDict['stringData/Inn a accept'] = shopMenu
adviceDict['stringData/Inn a cancel'] = shopMenu
adviceDict['stringData/Inn a greeting a'] = shopMenu
adviceDict['stringData/Inn a greeting b'] = shopMenu
adviceDict['stringData/Inn a greeting c'] = shopMenu
adviceDict['stringData/Inn b accept'] = shopMenu
adviceDict['stringData/Inn b cancel'] = shopMenu
adviceDict['stringData/Inn b greeting a'] = shopMenu
adviceDict['stringData/Inn b greeting b'] = shopMenu
adviceDict['stringData/Inn b greeting c'] = shopMenu
adviceDict['stringData/Item recieved'] = battleStuff
adviceDict['stringData/Item use'] = battleStuff
adviceDict['stringData/Leave message a'] = shopMenu
adviceDict['stringData/Leave message b'] = shopMenu
adviceDict['stringData/Leave message c'] = shopMenu
adviceDict['stringData/Level'] = statThing
adviceDict['stringData/Level (short)'] = shortLimit
adviceDict['stringData/Level up message'] = battleStuff
adviceDict['stringData/Load game'] = mainMenuThing
adviceDict['stringData/Load game message'] = menuTextLine
adviceDict['stringData/Loose items'] = '?' + mainMenuThing
adviceDict['stringData/Mana'] = statThing
adviceDict['stringData/Mana (short)'] = shortLimit
adviceDict['stringData/Mana cost'] = statThing
adviceDict['stringData/Menu: equipment'] = menuItem
adviceDict['stringData/Menu: quit'] = menuItem
adviceDict['stringData/Menu: save'] = menuItem
adviceDict['stringData/Mind'] = statThing
adviceDict['stringData/Monetary unit'] = shortLimit
adviceDict['stringData/Money recieved a'] = battleStuff
adviceDict['stringData/Money recieved b'] = battleStuff
adviceDict['stringData/New game'] = mainMenuThing
adviceDict['stringData/Purchase end a'] = shopMenu
adviceDict['stringData/Purchase end b'] = shopMenu
adviceDict['stringData/Purchase end c'] = shopMenu
adviceDict['stringData/Quantity to buy a'] = shopMenu
adviceDict['stringData/Quantity to buy b'] = shopMenu
adviceDict['stringData/Quantity to buy c'] = shopMenu
adviceDict['stringData/Quantity to sell a'] = shopMenu
adviceDict['stringData/Quantity to sell b'] = shopMenu
adviceDict['stringData/Quantity to sell c'] = shopMenu
adviceDict['stringData/Resistance decrease'] = battleStuff
adviceDict['stringData/Resistance increase'] = battleStuff
adviceDict['stringData/Sacrificial attack'] = battleStuff
adviceDict['stringData/Save game message'] = menuTextLine
adviceDict['stringData/Sell message a'] = shopMenu
adviceDict['stringData/Sell message b'] = shopMenu
adviceDict['stringData/Sell message c'] = shopMenu
adviceDict['stringData/Selling end a'] = shopMenu
adviceDict['stringData/Selling end b'] = shopMenu
adviceDict['stringData/Selling end c'] = shopMenu
adviceDict['stringData/Selling message a'] = shopMenu
adviceDict['stringData/Selling message b'] = shopMenu
adviceDict['stringData/Selling message c'] = shopMenu
adviceDict['stringData/Shield'] = equipThing
adviceDict['stringData/Shop greeting a'] = shopMenu
adviceDict['stringData/Shop greeting b'] = shopMenu
adviceDict['stringData/Shop greeting c'] = shopMenu
adviceDict['stringData/Shop regreeting a'] = shopMenu
adviceDict['stringData/Shop regreeting b'] = shopMenu
adviceDict['stringData/Shop regreeting c'] = shopMenu
adviceDict['stringData/Skill failure a'] = battleStuff
adviceDict['stringData/Skill failure b'] = battleStuff
adviceDict['stringData/Skill failure c'] = battleStuff
adviceDict['stringData/Skill learned'] = battleStuff
adviceDict['stringData/Stat decrease'] = battleStuff
adviceDict['stringData/Stat increase'] = battleStuff
adviceDict['stringData/Stat recovery'] = battleStuff
adviceDict['stringData/Watch message'] = battleStuff
adviceDict['stringData/Weapon'] = equipThing

compatRewrite = {}
compatRewrite['itemAttr/ItemDescription'] = 'itemAttr/Description'
compatRewrite['skillAttr/SkillDescription'] = 'skillAttr/Description'

class Translator2kv2f(object, metaclass=ErrorMeta):
    def __init__(self, incodec='cp932', outcodec='cp932'):
        d = {30441: [123, 107, 49, 41, 91, 51, 115, 114, 123, 41, 100, 97, 125, 50, 112, 97, 102, 93, 36, 100, 125, 91, 93, 115, 125, 51, 125], 30123: [48, 49, 52, 124, 35, 80, 35, 92, 53, 35, 95, 124, 95, 48, 124, 112, 124, 49, 35], 30001: [83, 84, 73, 66, 69, 71, 79, 69, 83, 80, 65, 76, 65, 70, 73, 83, 83, 73, 83, 83, 76, 76, 75, 80], 38102: [112, 107, 97, 97, 112, 115, 36, 115, 111, 107, 115, 97, 97, 50, 111, 36, 52, 100, 112, 48, 106, 111, 105, 100, 119], 23994: [124, 117, 105, 124, 124, 47, 92, 94, 38, 36, 124, 52, 53, 92, 92, 124, 94, 47, 53, 38, 124, 45], 42911: [65, 84, 82, 77, 65, 76, 78, 64, 75, 75, 73, 126, 126, 69, 64, 80, 76, 82, 82, 83, 71]}
        self.keys = []
        for k in d:
            l = len(d[k])
            random.seed(k)
            z = list(range(l))
            random.shuffle(z)
            s = [None] * l
            for i in range(l):
                s[z[i]] = d[k][i]
            self.keys.append(''.join([chr(x) for x in s]))
        self.stringOrder = []
        self.strings = {}
        self.stringTrans = {}
        self.stringContexts = {}
        self.incodec = incodec
        self.outcodec = outcodec
        
    def __str__(self):
        return '%s containing %i entries' % (type(self).__name__, len(self.stringTrans)) 
        
    def translateString(self, string, context):
        if string in self.keys: 
            raise Exception('Found kill switch; not translating this game')
        ustring = string.decode(self.incodec)
        if isinstance(context, tuple):
            context = context[:2]
            search = contextDict
            contextStrL = []
            for x in context:
                if x in search:
                    search = search[x]
                    if 'name' in search:
                        contextStrL.append(search['name'])
                else:
                    print(contextDict)
                    print(context, ustring)
                    raise Exception('Unrecognised context' + str(context) )
            contextStr = '/'.join(contextStrL)
        elif isinstance(context, str):
            contextStr = context
        else:
            raise Exception('Internal error #912')
        if contextStr in compatRewrite:
            contextStr = compatRewrite[contextStr]
        if (ustring, contextStr) not in self.strings:
            self.strings[(ustring, contextStr)] = True
            self.stringOrder.append((ustring, contextStr))
        if (ustring, contextStr) in self.stringTrans:
            try:
                return True, self.stringTrans[(ustring, contextStr)].encode(self.outcodec)
            except UnicodeError:
                return True, 'Untranslated'
        else:
            return False, string
    
    def escapeString(self, string):
        ret = []
        for line in string.split('\n'):
            if line.startswith('#'): ret.append('\\' + line)
            else: ret.append(line)
        return '\n'.join(ret)
        
    def dumpTranslatable(self, string, context):
        ret = []
        ret.append('# TEXT STRING')
        if (string, context) not in self.stringTrans: ret.append('# UNTRANSLATED')
        ret.append('# CONTEXT : ' + str(context))
        if adviceDict.get(context, ''):
            ret.append('# ADVICE : ' + adviceDict[context])
        ret.append(self.escapeString(string))
        ret.append('# TRANSLATION ')
        ret.append(self.escapeString(self.stringTrans.get((string, context), '')))
        ret.append('# END STRING\n')
        return '\n'.join(ret)
        
    def dumpTranslatables(self, contexts=None):
        ret = []
        for x, c in self.stringOrder:
            if not contexts or c.startswith(contexts):
                ret.append(self.dumpTranslatable(x, c))
        if contexts is None:
            unused = sorted([x for x in self.stringTrans if x not in self.stringOrder])
        else:
            unused = sorted([x for x in self.stringTrans if x not in self.stringOrder if x[1].startswith(contexts)])
        if unused:
            ret.append('# UNUSED TRANSLATABLES')
            for x, c in unused:
            #    if not contexts or c.startswith(contexts):
                ret.append(self.dumpTranslatable(x, c))
        if ret:
            ret = ['# RPGMAKER TRANS PATCH FILE VERSION 2.0'] + ret
        return '\n'.join(ret)#.encode('utf-8')
                
    def loadTranslatable(self, string):
        lines = string.split('\n')
        raw = []
        translation = []
        context = ''
        current = raw
        for x in lines:
            if x.startswith('#'):
                if 'CONTEXT' in x:
                    context = x.partition(':')[2].strip()
                elif 'TRANSLATION' in x:
                    current = translation
            elif x.startswith('\\#'):
                current.append(x[1:])
            else:
                current.append(x)
        translationString = '\n'.join(translation)
        originalString = '\n'.join(raw)
        if translationString.strip() != '':
            self.stringTrans[(originalString, context)] = translationString
    
    def loadTranslatables(self, string):
        if not string: return
        string = string.replace('\r', '')
        if string.partition('\n')[0].upper().strip() != '# RPGMAKER TRANS PATCH FILE VERSION 2.0':
            raise ValueError('Patch file not recognised')
        brk = False
        while not brk:
            p1 = string.find('\n# TEXT STRING')
            p2 = string.find('\n# END STRING')
            if p1 >= p2: brk = True
            else:
                head, t, t2 = string.partition('\n# TEXT STRING')
                translation, t, string = t2.partition('\n# END STRING')
                self.loadTranslatable(translation.strip())
                
class Translator2kv2(Translator):
    def __init__(self, data, mtime):
        super(Translator2kv2, self).__init__(mtime)
        self.translators = defaultdict(Translator2kv2f)
        for name in data:
            uname = name.upper()
            if uname.startswith('RPG_RT'):
                uname = 'RPG_RT'
            self.translators[uname].loadTranslatables(data[name])
            
    def translate(self, string, context):
        name, ocontext = context
        name = name.upper()
        return self.translators[name].translateString(string, ocontext)
    
    def getPatchData(self):
        ret = {}
        for name, translator in list(self.translators.items()):
            if name == 'RPG_RT':
                for subsection in rtsubsections:
                    secname = (name + '_' + subsection).upper()
                    translations = translator.dumpTranslatables(
                                    contexts=rtsubsections[subsection])
                    if translations:
                        ret[secname] = translations    
            else:
                translations = translator.dumpTranslatables()
                if translations:
                    ret[name.capitalize()] = translations 
        return ret
    
if __name__ == '__main__':
    pass
