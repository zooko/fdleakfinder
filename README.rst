

fd-leak-finder
==============

fd-leak-finder helps you figure out why your unix process is using up too many fds.

To use it, generate strace output with a command something like this::

   strace -q -a1 -s0 -ff -e trace=desc -tttT -ostrace.file $EXECUTABLE

Then pipe the resulting "strace.file.$PID" into fd-leak-finder's stdin.

CAVEATS
=======

It turns out that strace's representation of this stuff is much more
complicated than I thought, and I don't understand why some of
fd-leak-finder's computations turn out the way they do. You can see "xxx
weird" sorts of messages in fd-leak-finder. Hopefully it will be useful to
you anyway! If you figure out how to improve it please let me know.

I guess parsing strace's human-oriented output is a bad way to do this. I'm
not sure what a *good* way to do it is, on Linux. On Solaris or OSX I suppose
a good way to do it would be to use dtrace.

LICENCE
=======

You may use this package under the Simple Permissive Licence, version 1 or,
at your option, any later version. See the file COPYING.SPL.txt_ for the
terms of the Simple Permissive Licence, version 1.

.. _COPYING.SPL.txt: COPYING.SPL.txt

