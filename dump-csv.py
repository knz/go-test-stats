#!/usr/bin/env python3

import sys
#import math
import csv

allpackages = eval(sys.stdin.read())
alltests = []
for p in allpackages:
    alltests = alltests + p['tests']
    p['nsubtests'] = sum(len(t['subtests']) for t in p['tests'])

subtests = []
for t in alltests:
    for st in t['subtests']:
        st['testname'] = t['testname']
        st['pkgname'] = t['pkgname']
        subtests.append(st)


with open('packages.csv', 'w', newline='') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(['package','time','rtime','ctime','maxrss','maxcpu','maxth','nlines','ntests','nsubtests'])
    for p in allpackages:
        w.writerow([p['pkgname'], p['stats']['time'], p['rtime'], p['ctime'],
                    p['stats']['maxrss'],p['stats']['maxcpu'],p['stats']['maxth'],
                    p['stats']['nlines'],len(p['tests']),p['nsubtests']])

with open('tests.csv', 'w', newline='') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(['test','package','time','rtime','ctime','maxrss','maxcpu','maxth','nlines','nsubtests','result'])
    for p in alltests:
        w.writerow([p['testname'],p['pkgname'], p['stats']['time'], p['rtime'], p['ctime'],
                    p['stats']['maxrss'],p['stats']['maxcpu'],p['stats']['maxth'],
                    p['stats']['nlines'],len(p['subtests']),p['result']])

with open('subtests.csv', 'w', newline='') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(['test','package','rtime'])
    for p in subtests:
        w.writerow([p['testname']+'/'+p['sname'],p['pkgname'], p['rtime']])
