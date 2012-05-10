#!/usr/bin/env python
# encoding: utf-8
"""
boTimingCharts

Created by Bohdon Sayre on 2012-05-09.
Copyright (c) 2012 Bohdon Sayre. All rights reserved.
"""

from pymel.core import *
from butterfly.metanode import MetaNode
import butterfly.utils
import curves
import logging
import sys
import os

__all__ = [
    'GUI',
]

MAIN_NODE = 'btcTimingCharts'
CAM_NODE = 'btcCameraTransform'
CAM_ADJUST_NODE = 'btcCameraAdjust'
SKETCH_NODE = 'btcSketchingGrp'
PREF = 'btcTimingChartCommonPrefs'

TRANSFORM_ATTRS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

UPDATE_DURING_PLAYBACK = False

class GUI(object):
    def __init__(self):
        self.winName = 'btcWin'
        self.build()
    
    def build(self):
        if window(self.winName, ex=True):
            deleteUI(self.winName, wnd=True)
        
        with window(t='Timing Charts 0.61'):
            with columnLayout(adj=True, rs=2):
                button(l='Setup Timing Charts', c=Callback(setupTimingCharts, 'persp'))
                button(l='Remove Timing Charts', c=Callback(removeTimingCharts))
                button(l='Clear Timing Chart Preferences', c=Callback(clearPreferences))
                separator(h=4, st='none')
                button(l='Make Chart (select objects)', c=Callback(addChar))


def getTimingChartNode(create=False):
    if objExists(MAIN_NODE):
        return MetaNode(MAIN_NODE)
    elif create:
        return MetaNode(name=MAIN_NODE, nodeType='transform')


def setupTimingCharts(camera):
    if camera is None:
        camera = 'persp'
    # find camera
    try:
        node = PyNode(camera)
    except:
        LOG.error('Could not find camera: {0}'.format(camera))
        return
    # find main meta node
    chart = getTimingChartNode(create=True)
    # store selection so we can restore it
    sel = selected()
    
    # TODO: load prefs here
    
    chart['currentChart'] = ''
    chart['numRecogResponse'] = 0.25
    
    # add expression to update char during playback
    expression(s='tx=0;python("boTimingCharts.updateDuringPlayback()");', o=chart.node, ae=True, sn=True, n='timingChartsPlaybackUpdate_exp')
    
    # camera transform node
    camGrp = group(em=True, p=chart.node, n=CAM_NODE)
    for a in TRANSFORM_ATTRS:
        if a == 'tz':
            butterfly.utils.add(camera.attr(a), 1) >> camGrp.attr(a)
        else:
            camera.attr(a) >> camGrp.attr(a)
    chart['cameraTransform'] = camGrp
    
    # sketching group and curve
    sketchGrp = group(em=True, p=camGrp, n=SKETCH_NODE)
    sketchGrp.tz.set(-20)
    sketchGrp.s.set((10, 10, 10))
    sketchGrp.v.set(False)
    sketchRefCurve = curve(d=1, p=[(0, 0, 0), (0, 0, 0)], n='btcSketchRefCurve')
    sketchRefCurve.v.set(False)
    sketchRefCurve.setParent(camGrp)
    chart['sketchRefObj'] = sketchRefCurve
    
	# camera adjust node for film aperture and near clipping
	camAdjust = group(em=True, p=camGrp, n=CAM_ADJUST_NODE)
	camAdjust.sy.set(-1)
	camAdjust.addAttr('cameraFocalLength', at='double')
	expression(s='cameraFocalLength = {0}.focalLength;\nsx = -sy = -(35/cameraFocalLength);'.format(camera.getShape()), o=camAdjust, ae=True, sn=True, uc='all', n'{0}_exp'.format(camAdjust))
	
	# lock nodes
	for obj in (chart.node, camGrp, camAdjust, sketchGrp):
	    for a in TRANSFORM_ATTRS:
            obj.attr(a).setLocked(True)
        obj.v.setKeyable(False)
        obj.v.showInChannelBox(True)
    
    # setup contexts, etc
    setupSketchContexts()
    setupBreakdownRefs()
    setupScriptJobs()
    loadNumberRefs()    
	#//setup sketching context
	#btcSetup_sketchContexts;
	#//setup the default reference curves
	#btcSetup_sketchBreakdownRefs;
	#//setup selection checking script job
	#btcSetup_setupScriptJobs;
	#//load any saved number references
	#btcCtx_SketchNumbersLoadRefs;
	
	#brcmRegisterCondition("btcTimingChartsRMBCondition", 0);
	#brcmRegisterHitCondition("btcTimingChartsRMBHitCondition");
		
	savePreferences()
	
	select(sel)
	LOG.info('// Bo Timing Charts setup successfully!...')



def setupBreakdownRefs():
    """
    Create curves in the sketching group that are
    used to identify breakdown sketches.
    """
    chart = getTimingChartNode()
    if chart is None:
        return
    
    # build each version of the arcs
    names = ['halfLeft', 'halfRight', 'thirdLeft', 'thirdRight']
    divs = [2, 2, 3, 3]
    scales = [1, -1, 1, -1]
    
    for i in range(len(names)):
        name = names[i]
        div = divs[i]
        scale = scales[i]
        
        tmpCurves = []
        for j in range(div):
            crv = curves.buildArc(j/div, (j+1)/div)
            tmpCurves.append()
        
        attached = curves.attachCurve(tmpCurves)
		rebuilt = rebuildCurve(attached, s=60, d=1, tol=0.000000001, n='breakdownRef_{0}'.format(name))
		rebuilt.sx.set(scale)
		crv = btcUnitizeCurve(rebuilt)
		for a in TRANSFORM_ATTRS:
		    crv.attr(a).setLocked(False)
        crv.addAttr('numDivs', at='long')
        crv.numDivs.set(div)
        
        crv2 = duplicate(crv, rr=True)
        reverseCurve(crv2, ch=False, rpo=True)


def setupScriptJobs():
    """
    Create a scriptNode that contains script jobs for the Timing Charts
    """
	bscript = """
if (`exists btcSelectScriptJobProc` && `exists btcTimeChangeCheck`) {
    scriptJob -cu 1 -kws -e "SelectionChanged" "btcSelectScriptJobProc";
    scriptJob -cu 1 -kws -e "timeChanged" "btcTimeChangeCheck";
}
if (`exists btcFileOpenProc`)
    btcFileOpenProc;
    """
    
    ascript = """
btcKillScriptJobByName("SelectionChanged" "btcSelectScriptJobProc");
btcKillScriptJobByName("timeChanged" "btcTimeChangeCheck");
    """
    
    sn = scriptNode(bs=bscript, as=ascript, st=1, n='btcScriptJobs_sn')
    scriptNode(sn, eb=True)


def removeTimingCharts():
    chart = getTimingChartNode()
    if chart is not None:
        delete(chart.node)
    
    snodes = ls('*btcScriptJobs_sn*')
	if len(snodes) > 0:
		delete(snodes)

	//remove registered right click conditions
	source boRightClickManager;
	brcmRemoveCondition("btcTimingChartsRMBCondition");
	brcmRemoveHitCondition("btcTimingChartsRMBHitCondition");

	//global variables
	global int $btcTimingChartsSetup;
	global string $btcChartList[];
	$btcTimingChartsSetup = 0;
	clear $btcChartList;
}
global proc btcSaveTimingChartCommonPrefs() {
//saves common timing chart preferences like num response time

	optionVar -ca "btcTimingChartCommonPrefs";
	float $numRecogResponse = `getAttr ("btcTimingCharts.numRecogResponse")`;
	global int $btcAutoSelect_chartMainTitle;
	global int $btcAutoSelect_chartMainLine;
	global int $btcAutoSelect_arcCurve;
	global int $btcAutoSelect_lineCurve;
	global int $btcShowNumberTickers;
	optionVar -fva "btcTimingChartCommonPrefs" $numRecogResponse;
	optionVar -fva "btcTimingChartCommonPrefs" $btcAutoSelect_chartMainTitle;
	optionVar -fva "btcTimingChartCommonPrefs" $btcAutoSelect_chartMainLine;
	optionVar -fva "btcTimingChartCommonPrefs" $btcAutoSelect_arcCurve;
	optionVar -fva "btcTimingChartCommonPrefs" $btcAutoSelect_lineCurve;
	optionVar -fva "btcTimingChartCommonPrefs" $btcShowNumberTickers;

	//print ("//Timing Chart common preferences saved...\n");
}
global proc btcClearTimingChartPrefs() {
//removes all optionVars created by Bo Timing Charts

	string $optionVars[];
	$optionVars = {"btcChartColorDefaults",
					"btcNumSketchRefCurves",
					"btcTimingChartCommonPrefs"};

	for ($option in $optionVars) {
		optionVar -remove $option;
	}

	print ("// Timing Chart Preferences successfully removed...\n");
}