import copy, pprint, re, sys

def main():
    verbose = False
    if ('-v' in sys.argv) or ('--verbose' in sys.argv):
        verbose = True

    MORE_FDS_RES=[]

    OPEN_RE=re.compile("^[0-9 \.]*(?:open|openat)\((?P<fname>[^)]*)\) = (?P<fd>[0-9]+)")
    opexs=[]
    opexs.append('17354 1354663224.195562 open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3 <0.000012>')
    opexs.append('17355 1354663302.410648 openat(AT_FDCWD, "cli/Check/deep_check/servers/k6vb2bpd/storage/shares/o5/o57pfejnbckhndhyuzf2sz2j7i", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 312 <0.000013>')

    for ex in opexs:
        assert OPEN_RE.match(ex), ex
        int(OPEN_RE.match(ex).group('fd'))

    MORE_FDS_RES.append(OPEN_RE)

    OPEN_RESUMED_RE=re.compile("^[0-9 \.]*<\.\.\. (?:open|openat) resumed> \) = (?P<fd>[0-9]+)")
    opresexs=[]
    opresexs.append('17355 1354663302.423090 <... open resumed> ) = 312 <0.000024>')

    for ex in opresexs:
        assert OPEN_RESUMED_RE.match(ex), ex
        int(OPEN_RESUMED_RE.match(ex).group('fd'))

    MORE_FDS_RES.append(OPEN_RESUMED_RE)

    PIPE_RE=re.compile("^[0-9 \.]*(?:pipe|pipe2)\(\[(?P<fd>[0-9]+), (?P<fd2>[0-9]+)\].*\) = 0")
    pipeexs=[]
    pipeexs.append('24938 1354730397.165200 pipe([3, 4]) = 0 <0.000027>')
    pipeexs.append('1354739933.693083 pipe2([4, 5], O_CLOEXEC) = 0 <0.000022>')

    for ex in pipeexs:
        assert PIPE_RE.match(ex), ex
        int(PIPE_RE.match(ex).group('fd'))
        int(PIPE_RE.match(ex).group('fd2'))

    MORE_FDS_RES.append(PIPE_RE)

    # EPOLL_CTR_RE=re.compile("^[0-9 \.]*epoll_ctl\([0-9]+, [^,]+, (?P<fd>[0-9]+)")
    # epollctrexs=[]
    # epollctrexs.append('1354739952.683160 epoll_ctl(10, EPOLL_CTL_ADD, 7, {EPOLLIN, {u32=7, u64=22205092589469703}}) = 0 <0.000026>')
    # 
    # for ex in epollctrexs:
    #     assert EPOLL_CTR_RE.match(ex), ex
    #     int(EPOLL_CTR_RE.match(ex).group('fd'))
    # 
    # MORE_FDS_RES.append(EPOLL_CTR_RE)

    FEWER_FDS_RES=[]

    CLOSE_RE=re.compile("^[0-9 \.]*close\((?P<fd>[0-9]+)")

    FEWER_FDS_RES.append(CLOSE_RE)

    cloexs=[]
    cloexs.append('17354 1354663224.195705 close(3) = 0 <0.000008>')
    cloexs.append('17355 1354663302.422837 close(312 <unfinished ...>')
    cloexs.append('17355 1354663302.423566 close(312 <unfinished ...>')
    cloexs.append('1354739931.501748 close(3) = 0 <0.000008>')
    for RE in FEWER_FDS_RES:
        for cloex in cloexs:
            assert RE.match(cloex), cloex
            int(RE.match(cloex).group('fd'))

    # anti-example:
    antiexs=[]
    antiexs.append('17355 1354663302.423052 open("cli/Check/deep_check/servers/k6vb2bpd/storage/shares/o5/o57pfejnbckhndhyuzf2sz2j7i/2", O_RDONLY <unfinished ...>')
    antiexs.append('17354 1354663224.195173 open("/usr/local/lib/tls/x86_64/libpthread.so.0", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory) <0.000012>')

    for antiex in antiexs:
        assert not OPEN_RE.match(antiex), antiex
        assert not OPEN_RESUMED_RE.match(antiex), antiex
        assert not PIPE_RE.match(antiex), antiex
        # assert not EPOLL_CTR_RE.match(antiex), antiex
        assert not CLOSE_RE.match(antiex), antiex


    openfiles = {} # k: fd, v: (fname, inl)

    high_water_mark = None

    for inl in sys.stdin:
        for RE in MORE_FDS_RES:
            mo = RE.match(inl)
            if mo is not None:
                try:
                    fname = mo.group('fname')
                except IndexError:
                    fname = '<unknown>'
                try:
                    fd = int(mo.group('fd'))
                except ValueError, e:
                    e.args = tuple(e.args + (inl,))
                    raise
                assert not openfiles.has_key(fd), (fd, fname, inl, openfiles[fd])
                openfiles[fd] = (fname, inl)

                if verbose:
                    print "++ %d=>%s okay now there are %d, %s" % (fd, fname, len(openfiles), inl)

                if high_water_mark is None or len(openfiles) > len(high_water_mark):
                    high_water_mark = copy.copy(openfiles)

                try:
                    fd2 = int(mo.group('fd2'))
                except IndexError:
                    # okay nevermind
                    pass
                except ValueError, e:
                    e.args = tuple(e.args + (inl,))
                    raise
                else:
                    assert not openfiles.has_key(fd2), (fd2, fname, inl, openfiles[fd2])
                    openfiles[fd2] = (fname, inl)

                    if verbose:
                        print "++ %d=>%s okay now there are %d, %s" % (fd2, fname, len(openfiles), inl)

                    if high_water_mark is None or len(openfiles) > len(high_water_mark):
                        high_water_mark = copy.copy(openfiles)

                continue

        for RE in FEWER_FDS_RES:
            mo = RE.match(inl)
            if mo is not None:
                fd = int(mo.group('fd'))
                if openfiles.has_key(fd):
                    if verbose:
                        print "-- %d=>%s okay now there are %d, %s" % (fd, openfiles[fd], len(openfiles)-1, inl)
                    del openfiles[fd]
                else:
                    print "xxx weird fd: %d, inl: %s" % (fd, inl)
                continue

    print "--- high water mark: ", len(high_water_mark)
    pprint.pprint(high_water_mark)

if __name__ == '__main__':
    main()
