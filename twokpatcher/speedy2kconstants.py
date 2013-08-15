## BEGIN INLINE BLOCK
from nameDict import names, opcodes, stringDataDict
## END INLINE BLOCK

blockTypes = {# LDB File blocks
              'Hero': 11, 'Skill': 12, 'Item': 13, 'Monster': 14, 
              'MonsterParty': 15, 'Terrain': 16, 'Attribute': 17, 'Condition': 18,
              'Unknown0x13': 19, 'Unknown0x14': 20, 'Strings': 21, 'Unknown0x16': 22,
              'Switch': 23, 'Variables': 24, 'CommonEvents': 25,
              # LCF file blocks
              'Chipset': 1, 'MapWidth': 2, 'MapHeight': 3, 'LoopType': 11, 
              'ParallaxBG': 31, 'BGName': 32, 'HPan': 33, 'VPan': 34, 
              'HAutoPan': 35, 'HPanSpeed': 36, 'VAutoPan': 37, 'VPanSpeed': 38, 
              'LowerTiles': 71, 'UpperTiles': 72, 'EventsLayer': 81, 
              'TimesSaved': 91,
              }
              
contextNames = {'Hero': 'heroAttr', 'Skill': 'skillAttr', 'Item': 'itemAttr',
                'Condition': 'conditionDataAttr', 'Monster': 'monsterAttr',
                'MonsterParty': 'monsterPartyAttr', 'Attribute': 'attributeDataAttr',
                }

rtsubsections = {'HeroData': 'heroAttr', 'SkillData':'skillAttr', 'ItemData':'itemAttr', 
               'MonsterData':'monsterAttr', 'MonsterParties':'monsterPartyAttr',
               'attributeData':'attributeDataAttr', 'ConditionData': 'conditionDataAttr', 
               'StringData':'stringData', 'CommonEventData':'Dialogue'}
                       
scriptContainerSpecialKeys = {'commonEventContainer': (names['ComEventScriptLength'], names['ComEventScript']),
'monsterBattleEventPageContainer': (names['MonsterBattleScriptLength'], names['MonsterBattleScript']),
'mapEventPageContainer': (names['MapScriptLength'], names['MapScript'])
}

containerTypes = scriptContainerSpecialKeys.keys() + ['container']

lmuScripts = [
 ('MapScripts', ['MapScript'])
]
lmuScriptLens = [
 ('MapScripts', ['MapScriptLength'])
]

blockSchemaTypes = {'CommonEvents': 'commonEventContainer'}
                    
ldbTranslatables = [
 ('Hero', ['HeroName', 'ClassName', 'MagicName']),
 ('Skill', ['SkillName', 'SkillDescription', 'UsageText', 'UsageTextLine2', 'FailureMessage']),
 ('Item', ['ItemName', 'ItemDescription', 'UsageMessage']),
 ('Monster', ['MonsterName']),
 ('MonsterParty', ['MonsterPartyName']),
 ('Attribute', ['AttributeName']),
 ('Condition', ['ConditionName']),
]
ldbScripts = [
 ('CommonEvents', ['ComEventScript'])
]
ldbScriptLens = [
 ('CommonEvents', ['ComEventScriptLength'])
]

scriptStartCollects = [
 ('Change Hero Name', ['Change Hero Name', 'Change Hero Class'], 'SetStringVars'),
 ('Change Hero Class', ['Change Hero Name', 'Change Hero Class'], 'SetStringVars'),
 ('Message', ['Add line to message'], 'Message'),
 ('Show choice', [], 'ChoiceStarter'),
 ('Show choice option', [], 'Choice'),
]

scriptSchemaDict = {}
scriptSchemaStartCollectsDict = {}
for name, termnames, context in scriptStartCollects:
    scriptSchemaStartCollectsDict[opcodes[name]] = set([opcodes[x] for x in termnames]), context

scriptSchemaDict['startCollects'] = scriptSchemaStartCollectsDict
scriptSchemaDict['faceSelect'] = opcodes['Select message face']
scriptSchemaDict['message'] = opcodes['Message']
scriptSchemaDict['messageNextLine'] = opcodes['Add line to message']
scriptSchemaDict['choice'] = opcodes['Show choice']
scriptSchemaDict['nextChoice'] = opcodes['Show choice option']
scriptSchemaDict['endChoice'] = opcodes['End Choice block']
scriptSchemaDict['changename'] = opcodes['Change Hero Name']
scriptSchemaDict['changeclass'] = opcodes['Change Hero Class']

def getSchemaContainerDict(schema, name):
    if blockTypes[name] not in schema:
        containerType = blockSchemaTypes.get(containerName, 'container')
        schema[blockTypes[name]] = (containerType, {})
    return schema[blockTypes[name]][1]
    
ldbschemaDict = {}
contextDict = {}
for containerName, translatableStrings in ldbTranslatables:
    upd = dict([(names[x], ('string', {})) for x in translatableStrings])
    getSchemaContainerDict(ldbschemaDict, containerName).update(upd)
    if containerName in contextNames:
        z = {'name': contextNames[containerName]}
        contextDict[blockTypes[containerName]] = z
        for x in translatableStrings:
            z[names[x]] = {'name': x}
    
for containerName, scripts in ldbScripts:
    upd = dict([(names[x], ('script', scriptSchemaDict)) for x in scripts])
    getSchemaContainerDict(ldbschemaDict, containerName).update(upd)

for containerName, scriptsLens in ldbScriptLens:
    upd = dict([(names[x], ('scriptLength', {})) for x in scriptsLens])
    getSchemaContainerDict(ldbschemaDict, containerName).update(upd)

ldbschemaDict[blockTypes['MonsterParty']][1][names['MonsterPartyBattleEventPages']] = \
  ('monsterBattleEventPageContainer', 
  {names['MonsterBattleScript']: ('script', scriptSchemaDict),
   names['MonsterBattleScriptLength']: ('scriptLength', {})   
  })

ldbschemaDict[blockTypes['Strings']] = ('stringData', {'defaultStringData':stringDataDict})
#TODO: shouldn't use absolute 05 value

lmuschemaDict = {
 blockTypes['EventsLayer']: ('container', {
    05: ('mapEventPageContainer', {
      names['MapScriptLength']: ('scriptLength', {}),
      names['MapScript']: ('script', scriptSchemaDict)
    })
 })
}

lmuschema = ('blocks', lmuschemaDict)

ldbschema = ('blocks', ldbschemaDict)

schemas = {'\x0bLcfDataBase': ldbschema,
           '\x0aLcfMapUnit': lmuschema
}

if __name__ == '__main__':
    # TODO: Dump out schemas to a file and I don't have to do anything else!
    pass
    
