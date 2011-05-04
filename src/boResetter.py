'''
    Resetter
    2.1.2
    Python Version
    
    Copyright (c) 2010 Bohdon Sayre
    All Rights Reserved.
    bo@bohdon.com
    
    unique prefix: brst
    
    Description:
        This script allows you to setup controls for easy resetting,
        it stores the default values of any keyable attribute, and allows
        you to reset those attributes with a button or command
    
    Instructions:
        To run the script, use
            import boResetter
            boResetter.GUI()
    
    Version 2.1.2:
        > Rewrote main resetting method to use python evals, instead of using mel
        > Rewritten in python
        > Added channel box functionality - Set or reset the selected cb attributes using resetSmart or setDefaultsCB
        > Referencing and renaming now functional because the object name is not stored
        > Smart and Xform modes added
        > Popup menus to add each function to the current shelf
        > Includes listing, resetting, and removing of defaults
        > Adds a default string to selected objects for restoring attributes
    
    Feel free to email me with any bugs, comments, or requests!
'''
import maya.cmds as cmds

__version__ = '2.1.2'

#==============================================================================
def GUI():
    #window name
    win = 'brstWin';
    
    #define colors
    colSet = [0.3, 0.36, 0.49]
    colRemove = [0.49, 0.3, 0.3]
    colReset = [0.2, 0.2, 0.2]
    colReset2 = [0.25, 0.25, 0.25]
    
    #check for pre-existing window
    if cmds.window(win, ex=True):
        cmds.deleteUI(win, wnd=True)
    
    #create window
    cmds.window(win, rtf=1, mb=1, tlb=True, t='Resetter %s' % __version__)
    
    cmds.menu(l='Features')
    cmds.menuItem(l='Add reset buttons to shelf (coming)', en=False)
    cmds.menu(l='Info')
    cmds.menuItem(l='List All Objects and Defaults', c='boResetter.listDefaults(1)')
    cmds.menuItem(l='List Selected Object\'s Defaults', c='boResetter.listDefaults(0)')
    cmds.menuItem(l='List All Objects with Defaults', c='boResetter.listObjectsWithDefaults()')
    cmds.menuItem(l='Select All Objects with Defaults', c='boResetter.selectObjectsWithDefaults()')
    
    form = cmds.formLayout(nd=100)
    
    setFrame = cmds.frameLayout(l='Set/Remove Defaults', bs='out', mw=2, mh=2, cll=True, cl=True)
    cmds.columnLayout(rs=2, adj=True)
    b1 = cmds.button(l='Set Defaults', c='boResetter.setDefaults()', bgc=colSet)
    b2 = cmds.button(l='Set Defaults Use Selected Attrs', c='boResetter.setDefaultsCB()', bgc=colSet)
    b3 = cmds.button(l='Set Defaults Include Non-Keyable', c='boResetter.setDefaultsNonkeyable()', bgc=colSet)
    b4 = cmds.button(l='Remove Defaults', c='boResetter.removeDefaults(0)', bgc=colRemove)
    b5 = cmds.button(l='Remove from All Objects', c='boResetter.removeDefaults(1)', bgc=colRemove)
    
    cmds.setParent(form)
    
    resetFrame = cmds.frameLayout(l='Reset', bs='out', mw=2, mh=2)
    resetForm = cmds.formLayout(nd=100)
    b6 = cmds.button(l='Smart', c='boResetter.resetSmart(0)', bgc=colReset)
    b7 = cmds.button(l='Defaults', c='boResetter.resetDefault(0)', bgc=colReset)
    b8 = cmds.button(l='All', c='boResetter.resetDefault(1)', bgc=colReset2)
    cmds.formLayout(resetForm, e=True, ap=[(b6, 'left', 0, 0), (b6, 'right', 2, 33),
                                           (b7, 'left', 2, 33), (b7, 'right', 2, 66),
                                           (b8, 'left', 2, 66), (b8, 'right', 2, 100),
                                          ])
    
    
    mw=4
    cmds.formLayout(form, e=True, af=[(setFrame, 'left', mw), (setFrame, 'right', mw),
                                      (resetFrame, 'left', mw), (resetFrame, 'right', mw),
                                     ],
                                  ac=[(resetFrame, 'top', 2, setFrame),
                                     ], )
                                      
    
    cmds.window(win, e=True, h=100, w=205)
    if cmds.windowPref('brstWin', ex=True):
        cmds.windowPref('brstWin', e=True, h=100, w=205)
    cmds.showWindow(win)
#==============================================================================



#==============================================================================
#SET DEFAULTS DEFINITIONS
def setDefaults():
    setDefaultsMain(1, 0, 0)
def setDefaultsNonkeyable():
    setDefaultsMain(1, 1, 0)
def setDefaultsCB():
    setDefaultsMain(0, 0, 1)

def setDefaultsMain(key=1, nonkey=0, cb=0):
    '''Main definition for setting defaults on the selected objects/cb attrs'''
    
    import maya.mel as mel
    
    selList = cmds.ls(r=1, l=1, sl=1)
    if not selList: return
    if not key and not nonkey and not cb: return
    
    for obj in selList:
        attrList = []
        if key:
            tempList = cmds.listAttr(obj, u=1, k=1)
            if tempList is not None:
                attrList.extend(tempList)
        if nonkey:
            tempList = cmds.listAttr(obj, u=1, cb=1)
            if tempList is not None:
                attrList.extend(tempList)
        if cb:
            cbSelDict = getChannelBoxSelection()
            if obj in cbSelDict.keys():
                attrList.extend(cbSelDict[obj])
        
        if len(attrList) == 0:
            mel.eval("warning(\"no attributes of this type to set defaults for\");")
            return
        
        writeDefaultsAttr(obj, attrList)
    
    print('// set defaults for %d object(s), %d attribute(s)' % (len(selList), len(attrList)))

def writeDefaultsAttr(obj, attrList):
    '''Writes the current values of attrList on obj.
    Creates the brstDefaults attribute if it does not already exist'''
    
    objDefaults = {};
    if attrList is None:
        return
    
    for attr in attrList:
        #prepare string
        attrName = str(attr)
        attrVal = cmds.getAttr('%s.%s' % (obj, attr))
        attrType = cmds.getAttr('%s.%s' % (obj, attr), typ=True)
        if attrType == 'string':
            continue
        if type(attrVal) == list:
            #non-single attributes are returned as [(0.0, 0.0, 0.0)]
            objDefaults[attrName] = attrVal[0]
        else:
            objDefaults[attrName] = tuple([attrVal])
    
    #convert the dictionary into a string
    objDefaultsStr = str(objDefaults)
    
    #add the attribute if it doesn't exist
    if not cmds.objExists('%s.brstDefaults' % obj):
        cmds.addAttr(obj, ln='brstDefaults', dt='string')
    #set the attribute
    cmds.setAttr(('%s.brstDefaults' % obj), objDefaultsStr, type='string')
    
    print ('// default attribute settings for %s:\n%s\n' % (obj, objDefaultsStr))
#==============================================================================



#==============================================================================
#RESETTING DEFINITIONS
def resetSmart(all=0):
    resetMain('smart', (all and 'all' or 'selected'))
def resetDefault(all=0):
    resetMain('reset', (all and 'all' or 'selected'))
def resetXform(all=0):
    resetMain('xform', (all and 'all' or 'selected'))
def removeDefaults(all=0):
    resetMain('remove', (all and 'all' or 'selected'))
def listDefaults(all=0):
    resetMain('list', (all and 'all' or 'selected'))
def resetMain(modeStr, objSetStr):
    '''
        modeStr:
            list = print defaults
            reset = reset to defaults
            remove = remove defaults
            smart = reset, or do reset transforms (only works on selected)
            xform = reset transforms no matter what (only works on selected)
        objSetStr:
            selected = 0 = act on selected objects
            all = 1 = act on all objects
    '''
    
    list = modeStr == 'list'
    reset = modeStr == 'reset'
    remove = modeStr == 'remove'
    smart = modeStr == 'smart'
    xform = modeStr == 'xform'
    
    all = objSetStr == 'all'
    selected = objSetStr == 'selected'
    
    #reset smart and xform requires selected objects only
    if smart or xform:
        all = False
        selected = True
    
    objList = cmds.ls(r=1, l=1, sl=selected)
    
    
    objectCount = 0
    cbSelList = getChannelBoxSelection()
    if len(cbSelList) > 0 and smart:
        #channel box resetting only happens in smart mode
        #get the objects from the channel box selection, check for their defaults, and reset only those attributes
        #we need to get an array for each object, so we can use each object and it's attributes individually...
        for obj in cbSelList.keys():
            attrList = cbSelList[obj]
            resetObjAttrs(obj, False, attrList)
    else:
        #cycle through the selected objects and look for defaults, unless the mode is xform
        for obj in objList:
            if cmds.objExists('%s.brstDefaults' % obj) and not xform:
                if list:
                    cmds.ScriptEditor()
                    print ('// default attribute settings for %s:\n%s\n' % (obj, cmds.getAttr('%s.brstDefaults' % obj)) )
                elif reset or smart:
                    resetObjAttrs(obj, True)
                elif remove:
                    cmds.deleteAttr('%s.brstDefaults' % obj)
                    
                objectCount += 1
            
            elif smart or xform:
                #reset transforms
                for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                    if cmds.getAttr('%s.%s' % (obj, attr), se=1):
                        cmds.setAttr('%s.%s' % (obj, attr),  int('s' in attr))
    
    
    if list:
        cmds.ScriptEditor()
        print ('// listed defaults for %d object(s)\n' % objectCount)
    if remove:
        print ('// removed defaults from %d object(s)\n' % objectCount)

def resetObjAttrs(obj, useDefaults=True, customAttrs=None):
    '''
    Sets an object to default values, whether they're
    brstDefaults or the common attribute defaults.
    '''
    
    #this holds the final list of attributes to loop through
    attrList = []
    
    #get the defaults, if they exist
    defaults = getDefaults(obj)
    
    if customAttrs is not None:
        attrList = customAttrs[:]
    if defaults is not None and useDefaults is True:
        attrList.extend(defaults.keys())
    
    #return if there are no attributes
    if attrList == []:
        return
    
    #print 'attrList: %s' % attrList
    
    for attr in attrList:
        if (defaults is not None) and (attr in defaults.keys()):
            #get the value for the attribute
            attrVal = defaults[attr]
            #print 'setting %s.%s to %s' % (obj, attr, attrVal)
            if len(attrVal) == 1:
                cmds.setAttr('%s.%s' % (obj, attr), attrVal[0], )
            elif len(attrVal) == 3:
                cmds.setAttr('%s.%s' % (obj, attr), attrVal[0], attrVal[1], attrVal[2], )
        else:
            #the attribute wasn't found in defaults,
            #so it has to be trans rot or scale, else skip
            if 'translate' in attr or 'rotate' in attr:
                cmds.setAttr('%s.%s' % (obj, attr),  0)
            elif 'scale' in attr or 'visibility' in attr:
                cmds.setAttr('%s.%s' % (obj, attr),  1)

def getAttrLongName(attr):
    '''
    Returns the long name of a given attribute
    '''

    convertList = {'tx':'translateX', 'ty':'translateY', 'tz':'translateZ', 'rx':'rotateX', 'ry':'rotateY', 'rz':'rotateZ', 'sx':'scaleX', 'sy':'scaleY', 'sz':'scaleZ', 'v':'visibility'}
    if attr in convertList.keys():
        return convertList[attr]
    else:
        return attr
#==============================================================================


#==============================================================================
#LIST/SELECT OBJS WITH DEFAULTS
def listObjectsWithDefaults():
    objectsWithDefaultsMain('list')
def selectObjectsWithDefaults():
    objectsWithDefaultsMain('select')

def objectsWithDefaultsMain(modeStr):
    '''
    Finds objects with brstDefaults and either
    lists them or selects them based on modeStr
    '''
    
    allObjs = cmds.ls(r=1, l=1)
    
    if modeStr == 'select':
        cmds.select(cl=1)
    
    if modeStr == 'list':
        cmds.ScriptEditor()
        print '\n'
    
    objectCount = 0
    for obj in allObjs:
        if cmds.objExists('%s.brstDefaults' % obj):
            if modeStr == 'select':
                cmds.select(obj, add=1)
            elif modeStr == 'list':
                print ('// %s' % obj)
            objectCount += 1
    
    if not objectCount:
        print ('// no objects found with defaults set\n')
    elif modeStr == 'list':
        print ('// total of %d objects...\n' % objectCount)
#==============================================================================



#==============================================================================
#some get definitions
def getDefaults(obj):
    '''
    Returns the the brstDefaults of an object, if they exist.
    Return value is in the form {'attrName': [attrValues], }
    '''
    if not cmds.objExists('%s.brstDefaults' % obj):
        return None
    
    defaults = eval( cmds.getAttr('%s.brstDefaults' % obj) )
    return defaults

def getChannelBoxSelection(main=1, shape=1, out=1, hist=1):
    '''
    Returns a dictionary {'obj1': [attr1, attr2], 'obj2': [attr1, attr2]}
    representing the current selection in the channel box.
    '''
    
    #get every list of channel box selections
    allLists = []
    if main:
        tempList = [cmds.channelBox('mainChannelBox', q=1, mol=1), cmds.channelBox('mainChannelBox', q=1, sma=1)]
        if tempList is not None:
            allLists.append(tempList)
    if shape:
        tempList = [cmds.channelBox('mainChannelBox', q=1, sol=1), cmds.channelBox('mainChannelBox', q=1, ssa=1)]
        if tempList is not None:
            allLists.append(tempList)
    if out:
        tempList = [cmds.channelBox('mainChannelBox', q=1, ool=1), cmds.channelBox('mainChannelBox', q=1, soa=1)]
        if tempList is not None:
            allLists.append(tempList)
    if hist:
        tempList = [cmds.channelBox('mainChannelBox', q=1, hol=1), cmds.channelBox('mainChannelBox', q=1, sha=1)]
        if tempList is not None:
            allLists.append(tempList)
    
    if len(allLists) == 0:
        return None
    
    #create the dict we'll return
    cbSelDict = {}
    for (objs, attrs) in allLists:
        if objs is None or attrs is None:
            continue
        for obj in objs:
            #add the object if it hasn't been already
            objStr = str(cmds.ls(obj, l=1)[0])
            if objStr not in cbSelDict.keys():
                cbSelDict[objStr] = []
            #add any attributes that exist for that object
            for attr in attrs:
                if cmds.objExists('%s.%s' % (objStr, attr)) and (attr not in cbSelDict[objStr]):
                    longAttr = cmds.attributeName('%s.%s' % (objStr, attr), l=1)
                    cbSelDict[objStr].append(str(longAttr))
    
    return cbSelDict
#==============================================================================