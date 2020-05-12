#!/usr/bin/env python3

import re
import sys
import codecs


class Trackable:
    def __init__(self):
        self.last_ts = None
        self.time = 0
        self.maxcpu = 0.0
        self.maxrss = 0
        self.maxth = 0
        self.nlines = 0
        self.nbytes = 0

    def update(self, time, rss, cpu, th, nb):
        if self.last_ts is not None:
            self.time += time - self.last_ts
        self.last_ts = time
        self.maxrss = max(self.maxrss, rss)
        self.maxcpu = max(self.maxcpu, cpu)
        self.maxth = max(self.maxth, th)
        self.nlines += 1
        self.nbytes += nb

    def stats(self):
        return {'time': self.time, 'maxrss': self.maxrss, 'maxcpu': self.maxcpu,
                'maxth': self.maxth, 'nlines': self.nlines, 'nbytes': self.nbytes}


class PkgRes(Trackable):
    def __init__(self):
        super().__init__()
        self.result = "UNKNOWN"
        self.pkgname = "UNKNOWN"
        self.tail = "UNKNOWN"
        self.rtime = -1
        self.tests = []
        pass

    def add(self, test):
        self.tests.append(test)

    def finish(self, result, pkgname, tail):
        if result.startswith('?') and 'no test files' not in tail:
            print("UNEXPECTED PKG RESULT:", result, pkgname, tail, file=sys.stderr)
        self.result = result
        self.pkgname = pkgname
        self.tail = tail
        if tail.endswith('s'):
            self.rtime = float(tail[:-1])

    def pkgresult(self):
        stats = self.stats()
        ctime = 0
        if self.rtime > 0 and stats['time'] > self.rtime:
            ctime = stats['time']-self.rtime
        if stats['time'] == 0 and self.rtime > 0:
            stats['time'] = self.rtime
        tres = []
        for t in self.tests:
            tres.append(t.testresult())

        return {'pkgname': self.pkgname, 'result': self.result, 'tail': self.tail,
                'rtime': self.rtime, 'ctime': ctime,
                'tests': tres,
                'stats': stats}


class TestRes(Trackable):
    def __init__(self, testname, parentpkg):
        super().__init__()
        self.testname = testname
        self.rtime = 0
        self.parentpkg = parentpkg
        self.result = 'UNKNOWN'
        self.tail = 'UNKNOWN'
        self.subtests = {}

    def finish(self, result, tail):
        self.result = result
        self.tail = tail
        if tail.endswith('s'):
            self.rtime = float(tail[:-1])

    def addsubtest(self, sname):
        self.subtests[sname] = {'result': 'UNKNOWN', 'sname': sname, 'tail': 'UNKNOWN', 'rtime': 0}

    def finishsubtest(self, result, sname, tail):
        subtest = {'result': result, 'sname': sname, 'tail': tail, 'rtime': 0}
        if tail.endswith('s'):
            subtest['rtime'] = float(tail[:-1])
        self.subtests[sname] = subtest

    def testresult(self):
        stats = self.stats()
        ctime = 0
        if self.rtime > 0 and stats['time'] > self.rtime:
            ctime = stats['time']-self.rtime
        if stats['time'] == 0 and self.rtime > 0:
            stats['time'] = self.rtime

        return {'testname': self.testname, 'result': self.result, 'tail': self.tail,
                'pkgname': self.parentpkg.pkgname,
                'rtime': self.rtime, 'ctime': ctime,
                'subtests': list(self.subtests.values()),
                'stats': stats}


inputfile = codecs.open(sys.argv[1], mode='r', encoding='utf-8', errors='replace')

lineprefix = re.compile(r'^(?P<time>\d+)\s+(?P<rss>\d+)\s+(?P<cpu>\d+\.\d+)\s+(?P<th>\d+) (?P<msg>.*)$')

pkgre = re.compile(r'^(?P<result>(?:FAIL|ok  |\?   ))\tgithub.com/cockroachdb/cockroach/pkg/(?P<pkgname>[^ \t]*)\t(?P<tail>.*)$')

testrunre = re.compile(r'^=== RUN   (?P<testname>(?:Test|Example)[^/]*)$')
testresre = re.compile(r'^--- (?P<result>FAIL|PASS|SKIP): (?P<testname>(?:Test|Example)[^/]*) (?:\((?P<tail>.*)\))?$')
subtestrunre = re.compile(r'^=== RUN   (?P<testname>(?:Test|Example)[^/]*)/(?P<stestname>[^ ]*)$')
subtestresre = re.compile(r'^--- (?P<result>FAIL|PASS|SKIP): (?P<testname>(?:Test|Example)[^/]*)/(?P<stestname>[^ ]*) (?:\((?P<tail>.*)\))?$')

allpackages = []
currentpkg = PkgRes()
currenttest = None
lasttest = None
for line in inputfile:
    # line = line.strip()
    m = lineprefix.match(line)
    if m is None:
        print("UNEXPECTED:", line, file=sys.stderr)
        continue
    time, rss, cpu, th, msg = int(m.group('time')), int(m.group('rss')), float(m.group('cpu')), int(m.group('th')), m.group('msg')
    currentpkg.update(time, rss, cpu, th, len(line))
    if currenttest is not None:
        currenttest.update(time, rss, cpu, th, len(line))
    # print("msg=%r" % msg, file=sys.stderr)
    m = pkgre.match(msg)
    if m is not None:
        result, pkgname, tail = m.group('result'), m.group('pkgname'), m.group('tail')
        currentpkg.finish(result, pkgname, tail)
        # print("XXX", currentpkg.pkgresult(), file=sys.stderr)
        allpackages.append(currentpkg.pkgresult())
        currentpkg = PkgRes()
        currenttest = None
        continue
    m = testrunre.match(msg)
    if m is not None:
        if currenttest is not None:
            # print("ABSORBED %r: %r" % (currenttest.testname, line), file=sys.stderr)
            lasttest = currenttest
            currenttest = None
            # This is possible if a test is emulating go test output
            # as a test result.
            # In that case, just count it as output
            # in the current test.
            # continue
        tn = m.group('testname')
        currenttest = TestRes(tn, currentpkg)
        currentpkg.add(currenttest)
        continue
    m = testresre.match(msg)
    if m is not None:
        nm = m.group('testname')
        if currenttest is None:
            print("NO TEST STARTED:", line, file=sys.stderr)
            continue
        if nm != currenttest.testname:
            # This is possible if a test is emulating go test output
            # as a test result.
            # In that case, just count it as output
            # in the current test.
            continue
            # print("MISMATCH: EXPECTED %r, got %r", currenttest.testname, nm, file=sys.stderr)
        currenttest.finish(m.group('result'), m.group('tail'))
        lasttest = currenttest
        currenttest = None
        # print("YYY", currenttest.testresult(), file=sys.stderr)
    # print("UNKNOWN:", line, file=sys.stderr)
    # print("ZZZ", line)
    m = subtestrunre.match(msg)
    if m is not None:
        tn = m.group('testname')
        if currenttest is None:
            currenttest = TestRes(tn, currentpkg)
            currentpkg.add(currenttest)
        if tn != currenttest.testname:
            # This is possible if a test is emulating go test output
            # as a test result.
            # In that case, just count it as output
            # in the current test.
            continue
            # print("MISMATCH: EXPECTED %r, got %r", currenttest.testname, nm, file=sys.stderr)
        currenttest.addsubtest(m.group('stestname'))
        continue
    m = subtestresre.match(msg)
    if m is not None:
        nm = m.group('testname')
        if lasttest is None:
            print("NO TEST STARTED:", line, file=sys.stderr)
            continue
        # print("ZZZ2", nm, lasttest.testname)
        if nm != lasttest.testname:
            # This is possible if a test is emulating go test output
            # as a test result.
            # In that case, just count it as output
            # in the current test.
            continue
            # print("MISMATCH: EXPECTED %r, got %r", currenttest.testname, nm, file=sys.stderr)
        lasttest.finishsubtest(m.group('result'), m.group('stestname'), m.group('tail'))
        # print("ZZZ3", len(lasttest.subtests))

#allpackages.append(currentpkg.pkgresult())

print("AT END", file=sys.stderr)

print(allpackages)


# Overall structure of a test output:
#
# === RUN   TestXXXX
# (optionally, more:)
# === RUN   TestXXXX/YYYY
# (at end)
# --- (PASS|FAIL|SKIP):  TestXXXX (dur)
# (optionally, more)
# --- (PASSS|FAIL|SKIP): TestXXXX/YYYY (dur)
# (at end of pkg)
# PASS|FAIL
# ok 
