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

class Gui(object):
    def __init__(self):
        if window('bsmWin', ex=True):
            deleteUI('bsmWin')
        
        with window('bsmWin', t='Smear {0}'.format(__version__)):
            with frameLayout(lv=False, bv=False, mw=10, mh=10):
                with formLayout(nd=100) as tmpForm:
                    with frameLayout(l='Settings', bs='etchedIn', mw=4, mh=4) as stngsFrame:
                        with formLayout(nd=100) as tmpForm2:
                            tw = 60
                            txt1 = text(l='Camera  ', al='right', w=tw)
                            camMenu = optionMenu()
                            btn1 = button(l='Refresh', h=20)
                            txt2 = text(l='Resolution  ', al='right', w=tw)
                            resX = intField(v=18)
                            txt3 = text(l='x')
                            resY = intField(v=12)
                            txt4 = text(l='Target  ', al='right', w=tw)
                            targetField = textField()
                            btn2 = button(l='<<<', h=20)
                            formLayout(tmpForm2, e=True,
                                af=[(txt1, 'left', 0), (txt1, 'top', 3), (camMenu, 'top', 0), (btn1, 'right', 0),
                                    (txt2, 'left', 0), (txt4, 'left', 0), (btn2, 'right', 0)],
                                ac=[(camMenu, 'left', 4, txt1), (camMenu, 'right', 4, btn1),
                                    (txt2, 'top', 7, camMenu), (resX, 'top', 4, camMenu), (txt3, 'top', 7, camMenu),
                                    (resY, 'top', 4, camMenu), (resX, 'left', 4, txt2), (txt3, 'left', 4, resX),
                                    (resY, 'left', 4, txt3),
                                    (txt4, 'top', 7, resX), (targetField, 'top', 4, resX), (btn2, 'top', 4, resX),
                                    (targetField, 'left', 4, txt4), (targetField, 'right', 4, btn2)],
                            )
                    with frameLayout(l='Geometry', bs='etchedIn', mw=4, mh=4) as geoFrame:
                        textScrollList()
                    btn1 = button(l='Create Smear', h=30, bgc=(0.75, 0.75, 0.75))
                    btn2 = button(l='Control Window', h=30, w=100, c=Callback(ControlGui))
                    formLayout(tmpForm, e=True,
                        af=[(stngsFrame, 'top', 0), (stngsFrame, 'left', 0), (stngsFrame, 'right', 0),
                            (geoFrame, 'left', 0), (geoFrame, 'right', 0), (btn1, 'left', 12),
                            (btn1, 'bottom', 0), (btn2, 'right', 12), (btn2, 'bottom', 0)],
                        ac=[(geoFrame, 'top', 4, stngsFrame), (geoFrame, 'bottom', 8, btn1),
                            (btn1, 'right', 8, btn2)],
                    )


class ControlGui(object):
    def __init__(self):
        if window('bsmControlWin', ex=True):
            deleteUI('bsmControlWin')
        
        with window('bsmControlWin', t='Smear Control {0}'.format(__version__)):
            pass

