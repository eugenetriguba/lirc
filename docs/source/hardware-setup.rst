Hardware Setup
==============

This package will work as long as you have a lirc daemon running. You can use
the ``version()`` method on the ``Client`` and see what version of the lirc
daemon is running.  However, in order to do anything useful (such as sending
IR codes), you'll need to have an IR emitter or transciever hooked up to your
computer and recognized by lirc.