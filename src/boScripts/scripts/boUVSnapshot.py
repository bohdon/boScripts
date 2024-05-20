"""
UV Snapshot Tool

Copyright (c) 2011 Bohdon Sayre
All Rights Reserved.
bo@bohdon.com
Credit to Nick Matthews, Marcus Ng, Chanelle de Nysschen for the idea!

Description:
    A GUI for outputting uv snapshots of multiple objects at once.
    Simple and efficient options for size and format.

Feel free to email me with any bugs, comments, or requests!
"""

__version__ = "1.0"

import os
import subprocess
import sys

import pymel.core as pm


class GUI(object):
    def __init__(self):
        self.winName = "boBatchUVWin"
        self.build()

    def build(self):
        if pm.window(self.winName, ex=True):
            pm.deleteUI(self.winName, wnd=True)

        if not pm.windowPref(self.winName, ex=True):
            pm.windowPref(self.winName, tlc=(200, 200))
        pm.windowPref(self.winName, e=True, w=240, h=180)

        with pm.window(self.winName, rtf=True, mb=False, mxb=False, t="UV Snapshot") as self.win:
            with pm.formLayout(nd=100) as form:
                sizeTxt = pm.text(l="Size")
                self.sizeField = pm.intField(v=1024, w=50)
                self.sizeSlider = pm.intSlider(w=100, min=4, max=13, v=10, s=1, dc=pm.Callback(self.updateSizeField))

                sep1 = pm.separator(h=4, st="in")
                typeTxt = pm.text(l="File Type")
                self.fmtOpts = pm.optionMenu(w=60)
                for x in ["iff", "jpg", "png", "tga", "tif"]:
                    pm.menuItem(l=x)
                self.fmtOpts.setValue("tif")

                self.antiAliasCheck = pm.checkBox(l="Anti-Alias Lines", v=True, al="left")

                sep2 = pm.separator(h=4, st="in")
                self.dstOpts = pm.optionMenu(l="Destination", w=175)
                for x in ["sourceimages", "images"]:
                    pm.menuItem(l=x)
                pm.popupMenu(p=self.dstOpts, mm=True, b=3)
                pm.menuItem("Open", c=pm.Callback(self.openDir))

                infoTxt1 = pm.text(en=False, al="center", l="files will be saved as uvOut_objectName.ext")

                runBtn = pm.button(
                    l="Output UVs",
                    ann="Select multiple objects, then click Output UVs",
                    c=pm.Callback(self.snapshot),
                    h=26,
                )

            pm.formLayout(
                form,
                e=True,
                af=[
                    (sizeTxt, "top", 12),
                    (self.sizeField, "top", 10),
                    (self.sizeSlider, "top", 12),
                    (sep1, "left", 8),
                    (sep1, "right", 8),
                    (sep2, "left", 8),
                    (sep2, "right", 8),
                    (infoTxt1, "left", 0),
                    (infoTxt1, "right", 0),
                    (runBtn, "bottom", 8),
                    (runBtn, "left", 8),
                    (runBtn, "right", 8),
                ],
                ap=[
                    (sizeTxt, "left", -88, 50),
                    (typeTxt, "left", -100, 50),
                ],
                ac=[
                    (self.sizeField, "left", 8, sizeTxt),
                    (self.sizeSlider, "left", 5, self.sizeField),
                    (sep1, "top", 9, sizeTxt),
                    (typeTxt, "top", 9, sep1),
                    (self.fmtOpts, "top", 6, sep1),
                    (self.fmtOpts, "left", 5, typeTxt),
                    (self.antiAliasCheck, "top", 8, sep1),
                    (self.antiAliasCheck, "left", 8, self.fmtOpts),
                    (sep2, "top", 6, self.fmtOpts),
                    (self.dstOpts, "top", 10, sep2),
                    (infoTxt1, "bottom", 8, runBtn),
                    (self.dstOpts, "left", -25, typeTxt),
                ],
            )

    def updateSizeField(self):
        self.sizeField.setValue(pow(2, self.sizeSlider.getValue()))

    def openDir(self):
        dst = self.dstOpts.getValue()
        projDir = pm.workspace(q=True, fn=True)
        outDir = os.path.join(projDir, dst)
        if os.path.isdir(outDir):
            if sys.platform == "win32":
                subprocess.Popen(["explorer.exe", os.path.normpath(outDir)])

    def snapshot(self):
        sel = pm.selected()
        dst = self.dstOpts.getValue()
        fmt = self.fmtOpts.getValue()
        size = self.sizeField.getValue()
        aa = self.antiAliasCheck.getValue()
        snapshot(sel, dst, fmt, size, aa)


def snapshot(objs, dst, fmt, size, aa):
    """
    Snapshot the given objects. Returns the exported images.

    `dst` -- destination directory for the images
    `fmt` -- the file format
    `size` -- the image resolution. should be a factor of 2
    `aa` -- whether to anti-alias the lines or not
    """
    # validate params
    if not isinstance(objs, list):
        objs = [objs]
    if len(objs) == 0:
        raise ValueError("No valid objects were given")
    if size > 8192:
        raise ValueError("Size is too large ({0}). Limit is 8192".format(size))
    # save sel
    prevSel = pm.selected()
    result = []
    projDir = pm.workspace(q=True, fn=True)
    outDir = os.path.join(projDir, dst)
    for obj in objs:
        pm.select(obj)
        outName = "uvOut_{0}.{1}".format(obj.shortName().replace(":", "_"), fmt)
        outPath = os.path.join(outDir, outName)
        pm.refresh()
        pm.uvSnapshot(o=True, aa=aa, ff=fmt, xr=size, yr=size, n=outPath)
        result.append(outPath)
    # reselect
    pm.select(prevSel)
    # print results
    if len(result) == 0:
        print("no uv snapshots were output..")
    else:
        print("output {0} uv snapshot(s) to /{1} successfully!".format(len(result), dst))
