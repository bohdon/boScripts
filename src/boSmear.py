"""
Smear

Copyright (c) 2011 Bohdon Sayre
All Rights Reserved.
bohdon@gmail.com

Description:
    Allows you to create a "2D" mesh warp on specified objects,
    controlled relative to a camera. This allows the creation of
    "smearing" effects seen in traditional animations.

Features:
    > Instant setup
    > Huge speed improvement by using much simpler connections from the mesh control
    > Easy to use control window for managing all smear meshes
    > More mesh controls (soften, weight, etc)

Feel free to email me with any bugs, comments, or requests!
"""

from pymel.core import *

__version__ = '3.0.0dev'

class SmearError(Exception):
    pass

class Gui(object):
    camera_ann = 'The camera on which to apply the smear. This can be changed later.'
    target_ann = 'The object to fix the center of the smear deformer to.'
    res_ann = 'The resolution of the smear mesh'
    def __init__(self):
        self.buildUI()
        self.loadInfo()
    
    def buildUI(self):
        if window('bsmWin', ex=True):
            deleteUI('bsmWin')
        
        with window('bsmWin', t='Smear {0}'.format(__version__)):
            with frameLayout(lv=False, bv=False, mw=10, mh=10):
                with formLayout(nd=100) as mainForm:
                    with frameLayout(l='Settings', bs='etchedIn', mw=4, mh=4, bgc=(0.2, 0.2, 0.2)) as stngsFrame:
                        with formLayout(nd=100) as tmpForm:
                            tw = 60
                            camTxt = text(l='Camera  ', al='right', w=tw)
                            camMenu = self.uiCamMenu = optionMenu()
                            btn1 = button(l='Refresh', h=20, w=54, c=Callback(self.loadInfo))
                            targetTxt = text(l='Target  ', al='right', w=tw)
                            targetField = self.uiTargetField = textField()
                            btn2 = button(l='<<<', h=20, w=54, c=Callback(self.getTarget))
                            resTxt = text(l='Resolution  ', al='right', w=tw)
                            resX = self.uiResXField = intField(v=18, min=1, max=100, w=30)
                            resDivTxt = text(l='x')
                            resY = self.uiResYField = intField(v=12, min=1, max=100, w=30)
                            formLayout(tmpForm, e=True,
                                af=[(camTxt, 'left', 0), (camTxt, 'top', 3), (camMenu, 'top', 0), (btn1, 'right', 0),
                                    (resTxt, 'left', 0), (targetTxt, 'left', 0), (btn2, 'right', 0)],
                                ac=[(camMenu, 'left', 4, camTxt), (camMenu, 'right', 2, btn1),
                                    (targetTxt, 'top', 7, camMenu), (targetField, 'top', 4, camMenu), (btn2, 'top', 4, camMenu),
                                    (targetField, 'left', 4, targetTxt), (targetField, 'right', 2, btn2),
                                    (resTxt, 'top', 7, targetField), (resX, 'top', 4, targetField), (resDivTxt, 'top', 7, targetField),
                                    (resY, 'top', 4, targetField), (resX, 'left', 4, resTxt), (resDivTxt, 'left', 4, resX),
                                    (resY, 'left', 4, resDivTxt)],
                            )
                    with frameLayout(l='Geometry', bs='etchedIn', mw=4, mh=4, bgc=(0.2, 0.2, 0.2)) as geoFrame:
                        with formLayout() as tmpForm:
                            geoList = self.uiGeoList = textScrollList(ams=True)
                            btn1 = button(l='+', w=30, c=Callback(self.addGeo))
                            btn2 = button(l='-', w=30, c=Callback(self.delGeo))
                            formLayout(tmpForm, e=True,
                                af=[(geoList, 'top', 0), (geoList, 'left', 0), (geoList, 'bottom', 0),
                                    (btn1, 'top', 0), (btn1, 'right', 0), (btn2, 'right', 0)],
                                ac=[(geoList, 'right', 2, btn1), (btn2, 'top', 0, btn1)],
                            )
                    btn1 = button(l='Create Smear', h=30, bgc=(0.75, 0.75, 0.75), c=Callback(self.create))
                    btn2 = button(l='Control Window', h=30, w=100, c=Callback(ControlGui))
                    formLayout(mainForm, e=True,
                        af=[(stngsFrame, 'top', 0), (stngsFrame, 'left', 0), (stngsFrame, 'right', 0),
                            (geoFrame, 'left', 0), (geoFrame, 'right', 0), (btn1, 'left', 12),
                            (btn1, 'bottom', 0), (btn2, 'right', 12), (btn2, 'bottom', 0)],
                        ac=[(geoFrame, 'top', 10, stngsFrame), (geoFrame, 'bottom', 8, btn1),
                            (btn1, 'right', 10, btn2)],
                    )
    
    def loadInfo(self):
        """Populate the camera list with all perspective cams in the scene"""
        cams = [c.getParent() for c in ls(type='camera') if not c.isOrtho()]
        curVal = self.uiCamMenu.getValue()
        self.uiCamMenu.clear()
        self.uiCamMenu.addItems(cams)
        if curVal in cams:
            self.uiCamMenu.setValue(curVal)
    
    def getTarget(self):
        """Set the target object to the selected node"""
        obj = selected()
        if obj != []:
            self.uiTargetField.setText(str(obj[0]))
        else:
            self.uiTargetField.setText('')
    
    def addGeo(self):
        """Add the selected geometry to the geometry list"""
        items = self.uiGeoList.getAllItems()
        items.extend([str(i) for i in selected() if self.isGeo(i)])
        new = sorted(list(set(items)))
        print new
        self.uiGeoList.removeAll()
        self.uiGeoList.append(new)
    
    def isGeo(self, obj):
        """
        Return true if the object is the shape or
        transform of a deformable geometry
        """
        shapes = [obj]
        if obj.type() == 'transform':
            shapes = obj.getShapes()
        for shape in shapes:
            if 'deformableShape' in shape.type(i=True):
                return True
    
    def delGeo(self):
        """Deleted the selected geometry from the list"""
        items = self.uiGeoList.getSelectItem()
        for item in items:
            self.uiGeoList.removeItem(item)
    
    def create(self):
        cam = PyNode(self.uiCamMenu.getValue())
        target = PyNode(self.uiTargetField.getText())
        res = [self.uiResXField.getValue(), self.uiResYField.getValue()]
        geo = [PyNode(x) for x in self.uiGeoList.getAllItems()]
        s = Smear(cam, target, res, geo)
        s.create()


class ControlGui(object):
    def __init__(self):
        if window('bsmControlWin', ex=True):
            deleteUI('bsmControlWin')
        
        with window('bsmControlWin', t='Smear Control {0}'.format(__version__)):
            pass



class Smear(object):
    def __init__(self, cam, target, res, geo=None):
        """
        ``cam`` -- the camera to attach the smear mesh to
        ``target`` -- the node to attach the center of the deformer to
        ``res`` -- the resolution of the smear mesh ie. (18, 12)
        ``geo`` -- a list of all geometry to be affected by the smear
        """
        self.cam = cam
        self.target = target
        self.res = res
        self.geo = geo
    
    def create(self):
        self._validateObjs()
        self._createHierarchy()
        self._createLattice()
        #self.createAttrs()
        #self.createMesh()
    
    def _validateObjs(self):
        pass
    
    def _createHierarchy(self):
        self.mainGrp = group(em=True, n='smear_grp#')
        self.camChild = group(em=True, n='smear_camChild', p=self.mainGrp)
        self.meshOffset = group(em=True, n='smear_mesh_offset', p=self.camChild)
        self.meshScale = group(em=True, n='smear_mesh_scale', p=self.meshOffset)
        self.latticeFollow = group(em=True, n='smear_lattice_follow', p=self.camChild)
        self.latticeScale = group(em=True, n='smear_lattice_scale', p=self.latticeFollow)
    
    def _createLattice(self):
        ffd, self.lattice, base = lattice(ignoreSelected=True, dv=self.res + [2], ldv=(4, 4, 4), cp=True, s=(1, 1, 1), n='smear#', pos=(0, 0, 0))
        self.latticeGrp = self.lattice.getParent()
        # when a lattice is made, the vertex points are absolute, if a deformer
        # (such as a cluster) is applied a latticeShapeOrig is created which
        # maintains the absolute positions. the deformer could then be deleted
        # and the lattice points would remain zeroed. this is necessary for us
        # to connect them to the mesh points which will also be zeroed
        select(self.lattice.pt[0][0][0])
        newC = cluster(relative=True, envelope=1)
        delete(newC)
        #move into hierarchy
        parent(self.latticeGrp, self.latticeScale)
        resX, resY = self.res
        sX = 1.0275 * float(resX+2)/resX
        sY = 0.58 * float(resY+2)/resY
        self.latticeGrp.scaleX.set(sX)
        self.latticeGrp.scaleY.set(sY)
        self.latticeGrp.visibility.set(False)


