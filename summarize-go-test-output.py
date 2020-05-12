#!/usr/bin/env python3

import sys
import humanize
import math

numentries = 10
if len(sys.argv) > 1:
    numentries = int(sys.argv[1])

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

print("total number of packages:", len(allpackages))
print("total number of tests:", len(alltests))
print("total number of subtests:", len(subtests))

allpackages.sort(key=lambda x:-x['stats']['time'])
print()
print("packages with longest test durations:")
for p in allpackages[:numentries]:
    t = p['stats']['time']
    if t < 0:
        dur = '?'
    else:
        m = t // 60
        s = t % 60
        dur = "(%dm%ds)" % (m,s)
    print("%11d %8s %s" % (t, dur, p['pkgname']))

allpackages.sort(key=lambda x:-x['stats']['nbytes'])
print()
print("packages with largest test logs:")
for p in allpackages[:numentries]:
    s = p['stats']['nbytes']
    h = '(' + humanize.naturalsize(s,binary=True) + ')'
    print("%11d %8s %s" % (s, h, p['pkgname']))

allpackages.sort(key=lambda x:-x['stats']['maxrss'])
print()
print("largest memory usage (RSS peak) per package:")
for p in allpackages[:numentries]:
    s = p['stats']['maxrss'] * 1024
    h = '(' + humanize.naturalsize(s,binary=True) + ')'
    print("%11d %8s %s" % (s, h, p['pkgname']))

allpackages.sort(key=lambda x:-x['stats']['maxcpu'])
print()
print("largest CPU usage per package:")
for p in allpackages[:numentries]:
    c = p['stats']['maxcpu']
    nc = "(%dc)" % int(math.ceil(c / 100.))
    print("%11.2f %8s %s" % (c, nc, p['pkgname']))

allpackages.sort(key=lambda x:-len(x['tests']))
print()
print("largest number of tests per package:")
for p in allpackages[:numentries]:
    print("%11d %8s %s" % (len(p['tests']), "", p['pkgname']))

allpackages.sort(key=lambda x:-x['nsubtests'])
print()
print("largest number of subtests per package:")
for p in allpackages[:numentries]:
    print("%11d %8s %s" % (p['nsubtests'], "", p['pkgname']))

allpackages.sort(key=lambda x:-x['stats']['time']/(len(x['tests'])==0 and 1 or len(x['tests'])))
print()
print("packages with largest average time per test:")
for p in allpackages[:numentries]:
    t = p['stats']['time']/(len(p['tests'])==0 and 1 or len(p['tests']))
    if t < 0:
        dur = '?'
    else:
        m = t // 60
        s = t % 60
        dur = "(%dm%ds)" % (m,s)
    print("%11d %8s %s" % (t, dur, p['pkgname']))

allpackages.sort(key=lambda x:-x['stats']['nbytes']/(len(x['tests'])==0 and 1 or len(x['tests'])))
print()
print("packages with largest avg log sizes per test:")
for p in allpackages[:numentries]:
    n = p['stats']['nbytes']/(len(p['tests'])==0 and 1 or len(p['tests']))
    h = '(' + humanize.naturalsize(n,binary=True) + ')'
    print("%11d %8s %s" % (n, h, p['pkgname']))


def tname(t):
    return "%s.%s" % (t['pkgname'], t['testname'])

print()
print("tests with longest test durations:")
alltests.sort(key=lambda x:-x['stats']['time'])
for p in alltests[:numentries]:
    t = p['stats']['time']
    if t < 0:
        dur = '?'
    else:
        m = t // 60
        s = t % 60
        dur = "(%dm%ds)" % (m,s)
    print("%11d %8s %s" % (t, dur, tname(p)))

alltests.sort(key=lambda x:-x['stats']['nbytes'])
print()
print("tests with largest test logs:")
for p in alltests[:numentries]:
    s = p['stats']['nbytes']
    h = '(' + humanize.naturalsize(s,binary=True) + ')'
    print("%11d %8s %s" % (s, h, tname(p)))

alltests.sort(key=lambda x:-x['stats']['maxrss'])
print()
print("largest memory usage (RSS peak) per test:")
for p in alltests[:numentries]:
    s = p['stats']['maxrss'] * 1024
    h = '(' + humanize.naturalsize(s,binary=True) + ')'
    print("%11d %8s %s" % (s, h, tname(p)))

alltests.sort(key=lambda x:-x['stats']['maxcpu'])
print()
print("largest CPU usage per test:")
for p in alltests[:numentries]:
    c = p['stats']['maxcpu']
    nc = "(%dc)" % int(math.ceil(c / 100.))
    print("%11.2f %8s %s" % (c, nc, tname(p)))

alltests.sort(key=lambda x:-len(x['subtests']))
print()
print("largest number of subtests per test:")
for p in alltests[:numentries]:
    print("%11d %8s %s" % (len(p['subtests']), "", tname(p)))



def stname(t):
    return "%s.%s/%s" % (t['pkgname'], t['testname'], t['sname'])

print()
print("subtests with longest test durations:")
subtests.sort(key=lambda x:-x['rtime'])
for p in subtests[:numentries]:
    t = p['rtime']
    if t < 0:
        dur = '?'
    else:
        m = t // 60
        s = t % 60
        dur = "(%dm%ds)" % (m,s)
    print("%11d %8s %s" % (t, dur, stname(p)))
