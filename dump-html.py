#!/usr/bin/env python3

import sys
import humanize
import math

allpackages = eval(sys.stdin.read())
alltests = []
for p in allpackages:
    alltests = alltests + p['tests']
    p['nsubtests'] = sum(len(t['subtests']) for t in p['tests'])
    p['nskipped'] = sum(1 for t in p['tests'] if t['result'] == 'SKIP')

subtests = []
for t in alltests:
    for st in t['subtests']:
        st['testname'] = t['testname']
        st['pkgname'] = t['pkgname']
        subtests.append(st)

def tomag(n):
    if n < 1000:
        return '%d'%n
    if n < 1000000:
        return '%.1f K' % (n/1000.)
    return '%.1f M' % (n/1000000.)

def mdur(t):
    if t < 0:
        dur = '?'
    else:
        m = t // 60
        s = t % 60
        dur = "%dm%ds" % (m,s)
    return dur

with open('report.html', 'w') as h:
    h.write('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<script src='https://kryogenix.org/code/browser/sorttable/sorttable.js'></script>
<style type='text/css'>
table{width:100%;}
tr:hover{background-color:#ddd;}
table.pkg>tbody>tr>td:nth-child(2){text-align:right;}
table.pkg>thead>tr>th:nth-child(2){text-align:right;}
table.pkg>tbody>tr>td:nth-child(3){text-align:right;}
table.pkg>thead>tr>th:nth-child(3){text-align:right;}
table.pkg>tbody>tr>td:nth-child(4){text-align:right;}
table.pkg>thead>tr>th:nth-child(4){text-align:right;}
table.pkg>tbody>tr>td:nth-child(5){text-align:center;}
table.pkg>tbody>tr>td:nth-child(6){text-align:right;}
table.pkg>thead>tr>th:nth-child(6){text-align:right;}
table.pkg>tbody>tr>td:nth-child(7){text-align:center;}
table.pkg>tbody>tr>td:nth-child(8){text-align:right;}
table.pkg>thead>tr>th:nth-child(8){text-align:right;}
table.pkg>tbody>tr>td:nth-child(9){text-align:right;}
table.pkg>thead>tr>th:nth-child(9){text-align:right;}
table.pkg>tbody>tr>td:nth-child(10){text-align:center;}
table.pkg>tbody>tr>td:nth-child(11){text-align:center;}
table.pkg>tbody>tr>td:nth-child(12){text-align:center;}

table.tst>tbody>tr>td:nth-child(3){text-align:right;}
table.tst>thead>tr>th:nth-child(3){text-align:right;}
table.tst>tbody>tr>td:nth-child(4){text-align:right;}
table.tst>thead>tr>th:nth-child(4){text-align:right;}
table.tst>tbody>tr>td:nth-child(5){text-align:right;}
table.tst>thead>tr>th:nth-child(5){text-align:right;}
table.tst>tbody>tr>td:nth-child(6){text-align:center;}
table.tst>tbody>tr>td:nth-child(7){text-align:right;}
table.tst>thead>tr>th:nth-child(7){text-align:right;}
table.tst>tbody>tr>td:nth-child(8){text-align:center;}
table.tst>tbody>tr>td:nth-child(9){text-align:right;}
table.tst>thead>tr>th:nth-child(9){text-align:right;}
table.tst>tbody>tr>td:nth-child(10){text-align:right;}
table.tst>thead>tr>th:nth-child(10){text-align:right;}
table.tst>tbody>tr>td:nth-child(11){text-align:center;}
table.tst>tbody>tr>td:nth-child(12){text-align:center;}
</style>
</head>
<body>
<h1>Explanation</h1>
<ul>
<li>The table headings are clickable and sort the data.</li>
<li>"Time" is the observed run time.</li>
<li>"RTime" is the test run time as reported by Go's test runner.</li>
<li>"CTime" is the difference between Time and RTime, presumably compile time.</li>
<li>Max threads is the max observed number of OS threads (pthreads), not goroutines.</li>
</ul>
<hr>
<p><a name=packages><a href="">[Packages]</a><a href="#tests">[Tests]</a></p>
<h1>Packages</h1>
<table class="sortable pkg">
<thead>
<tr>
<th>Package</th>
<th>Time</th><th>RTime</th><th>CTime</th>
<th>Max cores used</th><th>Max RSS</th><th>Max threads</th>
<th>Log lines</th>
<th>Log size</th>
<th>Tests</th>
<th>Skipped</th>
<th>Subtests</th>
<th>Run tail</th>
</tr>
</thead>
<tbody>
''')
    for p in allpackages:
        t = p['stats']['time']
        dur = mdur(t)
        t2 = p['rtime']
        dur2 = mdur(t2)
        t3 = p['ctime']
        dur3 = mdur(t3)
        sz = p['stats']['maxrss'] * 1024
        hsz = humanize.naturalsize(sz,binary=True)
        c = p['stats']['maxcpu']
        nc = "%d" % int(math.ceil(c / 100.))
        lz = p['stats']['nbytes']
        hlz = humanize.naturalsize(lz,binary=True)
        h.write('''<tr><td>%s</td>''' % p['pkgname'])
        h.write('''<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>''' % (t, dur, t2, dur2, t3, dur3))
        h.write('''<td sorttable_customkey=%.2f>%s</td>
<td sorttable_customkey=%d>%s</td>''' % (       c, nc,
       sz, hsz))
        h.write('''<td>%d</td>
<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>
<td>%d</td>
<td>%d</td>
<td>%d</td>
<td>%s</td>''' % (
    p['stats']['maxth'],
    p['stats']['nlines'],  tomag(p['stats']['nlines']),
    lz, hlz,
    len(p['tests']),
    p['nskipped'],
    p['nsubtests'],
    p['tail'],
       ))
        h.write('</tr>\n')

    h.write('''</tbody></table>''')
    h.write('''
<hr>
<p><a name=tests><a href="#packages">[Packages]</a><a href="">[Tests]</a><a href="#subtests"></a></p>
<h1>Tests</h1>
<table class="sortable tst">
<thead>
<tr>
<th>Package</th>
<th>Test</th>
<th>Time</th><th>RTime</th><th>CTime</th>
<th>Max cores used</th><th>Max RSS</th><th>Max threads</th>
<th>Log lines</th>
<th>Log size</th>
<th>Subtests</th>
<th>Result</th>
<th>Run tail</th>
</tr>
</thead>
<tbody>
''')
    for p in alltests:
        t = p['stats']['time']
        dur = mdur(t)
        t2 = p['rtime']
        dur2 = mdur(t2)
        t3 = p['ctime']
        dur3 = mdur(t3)
        sz = p['stats']['maxrss'] * 1024
        hsz = humanize.naturalsize(sz,binary=True)
        c = p['stats']['maxcpu']
        nc = "%d" % int(math.ceil(c / 100.))
        lz = p['stats']['nbytes']
        hlz = humanize.naturalsize(lz,binary=True)
        h.write('''<tr><td>%s</td><td>%s</td>''' % (p['pkgname'],p['testname']))
        h.write('''<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>''' % (t, dur, t2, dur2, t3, dur3))
        h.write('''<td sorttable_customkey=%.2f>%s</td>
<td sorttable_customkey=%d>%s</td>''' % (       c, nc,
       sz, hsz))
        h.write('''<td>%d</td>
<td sorttable_customkey=%d>%s</td>
<td sorttable_customkey=%d>%s</td>
<td>%d</td>
<td>%s</td>
<td>%s</td>''' % (
    p['stats']['maxth'],
    p['stats']['nlines'],  tomag(p['stats']['nlines']),
    lz, hlz,
    len(p['subtests']),
    p['result'],
    p['tail'],
       ))
        h.write('</tr>\n')
    h.write('''</tbody></table>''')


    h.write('''</body></html>''')

