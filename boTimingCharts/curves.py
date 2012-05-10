#!/usr/bin/env python
# encoding: utf-8
"""
boTimingCharts.curves

Created by Bohdon Sayre on 2012-05-09.
Copyright (c) 2012 Bohdon Sayre. All rights reserved.
"""

from pymel.core import *

def buildArc(start, end, perfect=False):
    """
    Build a half circle curve with the given start and end range.
    The range is from 0 - 1. The smaller the range, the smaller the arc.
    
    `perfect` -- use a perferct arc, default is more visual appealing arc
    """
    start = min(max(start, 0), 1)
    end = min(max(end, start), 1)
    scale = end - start
    if scale == 0:
        raise ValueError('cannot create arc with scale 0')
    
    # each art has 7 points, scaled and offset
	if perfect:
	    pts = ((0, 0), (0.131, 0), (0.392, 0.108), (0.554, 0.5), (0.392, 0.892), (0.131, 1), (0, 1),)
	else:
	    pts = ((0, 0), (0.146, 0.028), (0.371, 0.182), (0.476, 0.5), (0.371, 0.818), (0.146, 0.972), (0. 1))
	pts = [(p[0]*scale, p[1]*scale + start) for p in pts]
	
	return curve(d=3, p=pts, k=(0, 0, 0, 1, 2, 3, 4, 4, 4), n='arcCurve')


def unitizeCurve(curve, grp, maxSpans=60):
    """
    Parent the given curve to group and scale/position it
    so that it fits within the groups 0 - 1 local space.
    """    
	curParent = curve.getParent()
	curve.setParent(grp)
	xform(curve, cp=True)
	
	center = xform(grp, q=True, ws=True, rp=True)
	move(curve, center, a=True, ws=True)
	relCenter = xform(curve, q=True, r=True, rp=True)
	curve.tx.set(-relCenter[0])
	curve.ty.set(-relCenter[1])
	
	bb = curve.getBoundingBox()
	# only scale x if the ratio is greator than .2, otherwise its probably a vertical line
	if bb.width()/bb.height() > 0.2:
	    curve.sx.set(1/bb.width())
	curve.sy.set(1/bb.height())
	
	makeIdentity(curve, apply=True, t=True, r=True, s=True, n=0)

	# rebuilding curves straight to $spans will sometimes result with a horrible curve
    # so we double the spans, until the double would be more than $spans, (then we just use $spans)
	for i in range(5): # max 5 iterations
	    spans = curve.getShape().spans.get()
	    newSpans = min(spans * 2, maxSpans)
	    curve = rebuildCurve(curve, newSpans)
	    if newSpans == maxSpans:
	        break
    
	return curve


def attachCurve(curves, ch=False, rpo=True, kmk=True, method=1, blendBias=0.5, bki=True, p=0.1, **kwargs):
    kw = locals().copy()
    kw.update(kwargs)
    curves = kw['curves']
    del kw['curves']
    del kw['kwargs']
    return attachCurve(curves, **kw)


def rebuildCurve(curve, s, d=3, ch=False, rpo=True, rt=1, end=1, kr=0, kcp=False, kep=True, kt=False, **kwargs):
    kw = locals().copy()
    kw.update(kwargs)
    curves = kw['curve']
    del kw['curve']
    del kw['kwargs']
    return rebuildCurve(curve, **kw)


