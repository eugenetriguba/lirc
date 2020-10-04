Configuring System LIRC
=======================

Once you have your IR emitter or transciever hooked
up to your computer, you'll want to configure the
system installed LIRC to ensure it works for emitting
IR.

You'll also want to ensure you have a configuration
file for the remote control that you want to emulate when
emitting IR since whatever you're sending IR to will likely
only understand IR codes from certain remotes.

This process will be different depending on the operating system you are using.
Below are instructions for Linux, Windows, and macOS. See the
`LIRC configuration guide <https://www.lirc.org/html/configuration-guide.html>`_
for more information. However, WinLIRC will be a bit different and you should read
their own resources if you are on Windows as well.

Linux
-----

LIRC configuration is typically in ``/etc/lirc/``. The two things you'll have to figure
out on your own is the ``lirc_options.conf`` file and adding your remote configuration
file as these are dependent on the hardware you use for your setup. However, I can give
general recommendations or what I typically do.

For ``lirc_options.conf``, the only change I make is to change the driver from
``devinput`` to ``default``. Devinput works fine for receiving IR, but it will not allow
you to emit IR. This driver is dependent on your hardware, but LIRC just works with
most devices on this driver nowadays.

For the remote configuration file, if you're using a common remote control, you may be
able to find it in the `LIRC remote control database <http://lirc.sourceforge.net/remotes/>`_.
Otherwise, you'll have to create it yourself. This can be done with
`LIRC's IR record utility <https://www.lirc.org/html/irrecord.html>`_. However, I've had much
better luck using a `RedRat3-II <http://lircredrat3.sourceforge.net/>`_ and RedRat's
`IR Signal Database <https://www.redrat.co.uk/software/ir-signal-database-utility/>`_ for creating
the remote configuration file. The RedRat3-II is now discontinued, although
`its driver's are still available <https://www.redrat.co.uk/support/firmware-drivers/>`_, but you
could look into the `RedRatX <https://www.redrat.co.uk/products/redrat-x/>`_ or see if you can
find a `RedRat3-II used <https://www.ebay.com/sch/i.html?_nkw=redrat3-ii&_sacat=0>`_. Place this
generated remote configuration file in your ``lircd.conf.d`` folder.

If you're using an Iguanaworks IR Transciever, you may find the discussion below useful. Basically,
the device should just work on the default driver.

  * https://github.com/iguanaworks/iguanair/issues/39

Windows
-------

You'll want to make sure you install WinLIRC at WinLIRC at http://winlirc.sourceforge.net/.
This is the LIRC port for Windows which corresponds with version 0.9.0 of LIRC. Past that,
you can run the WinLIRC executable file and select the "Input Plugin" for your device. Then,
you can select the remote configuration and click OK. You should now be able to select your remote
and send key codes. As long as the program is running in the background (it minimizes to the tray),
this package will be able to connect to it.

macOS
-----

On macOS, the paths are almost the same as the Linux ones, just prefixed with ``/opt/local/``.
Therefore, the LIRC configuration is typically at ``/opt/local/etc/lirc/`` and the lircd socket
is at ``/opt/local/var/run/lirc/lircd``

Refer to the Linux section for the rest of the configuration as they are almost the same besides
the ``/opt/local/`` prefix. However, on macOS, there is also no ``default`` driver like there is
on Linux. You'll have to figure out what devices will work and what driver it needs so you can
input that into ``lirc_options.conf``.


Example Remote Configuration File
---------------------------------

The following is an example of a remote configuration
file that would be placed inside of the ``lircd.conf.d/`` folder.
This is for a
`KENMORE_253-79081 <http://lirc.sourceforge.net/remotes/Kenmore/Kenmore_253_79081>`_,
remote taken from the `LIRC remote database <http://lirc.sourceforge.net/remotes>`_.

.. code-block:: text

  # Please make this file available to others
  # by sending it to <lirc@bartelmus.de>
  #
  # this config file was automatically generated
  # using lirc-0.9.0-pre1(default) on Sun Sep  7 00:53:46 2014
  #
  # contributed by Steven Shamlian
  #
  # brand: Kenmore
  # model no. of remote control: Unknown
  # devices being controlled by this remote: Kenmore 253.79081
  #
  # Kernel revision: 3.12.26+
  # Driver/device option: --driver default --device /dev/lirc0
  # Capture device:  Vishay TSOP6238 to Raspberry Pi GPIO pin 23
  # Kernel modules: lirc_rpi
  # Type of device controlled: Air Conditioner
  # Devices controlled: Kenmore 253.79081
  #
  # Remote Layout:
  #
  # /------------------------\
  # |KEY_POWER       KEY_TIME|
  # |                        |
  # |KEY_VOLUMEUP      KEY_UP|
  # |        KEY_PLAY        |
  # |KEY_VOLUMEDOWN  KEY_DOWN|
  # |        KEY_SAVE        |
  # |KEY_SHUFFLE    KEY_SLEEP|
  # |        KEY_PAUSE       |
  # \------------------------/
  # VOLUME keys are for fan speed
  # PLAY starts air conditioner
  # PAUSE makes unit fan-only
  # SAVE is Energy Saver mode
  # SHUFFLE is for Automatic Fan

  begin remote

    name  KENMORE_253-79081
    bits           16
    flags SPACE_ENC|CONST_LENGTH
    eps            30
    aeps          100

    header       9159  4455
    one           639  1615
    zero          639   486
    ptrail        637
    repeat       9103  2199
    pre_data_bits   16
    pre_data       0x10AF
    gap          108066
    toggle_bit_mask 0x0

        begin codes
            KEY_POWER                0x8877
            KEY_TIME                 0x609F
            KEY_VOLUMEUP             0x807F
            KEY_VOLUMEDOWN           0x20DF
            KEY_PLAY                 0x906F
            KEY_UP                   0x708F
            KEY_DOWN                 0xB04F
            KEY_SAVE                 0x40BF
            KEY_SHUFFLE              0xF00F
            KEY_SLEEP                0x00FF
            KEY_PAUSE                0xE01F
        end codes

  end remote

Example LIRC Options Configuration File
---------------------------------------

This is a ``lirc_options.conf`` file, taken
from ``/etc/lirc/lirc_options.conf`` on a
Linux machine, to get a feel for the configuration
options offered.

.. code-block:: text

  # These are the default options to lircd, if installed as
  # /etc/lirc/lirc_options.conf. See the lircd(8) and lircmd(8)
  # manpages for info on the different options.
  #
  # Some tools including mode2 and irw uses values such as
  # driver, device, plugindir and loglevel as fallback values
  # in not defined elsewhere.

  [lircd]
  nodaemon        = False
  driver          = default
  device          = auto
  output          = /var/run/lirc/lircd
  pidfile         = /var/run/lirc/lircd.pid
  plugindir       = /usr/lib/lirc/plugins
  permission      = 666
  allow-simulate  = No
  repeat-max      = 600
  #effective-user =
  #listen         = [address:]port
  #connect        = host[:port]
  #loglevel       = 6
  #release        = true
  #release_suffix = _EVUP
  #logfile        = ...
  #driver-options = ...

  [lircmd]
  uinput          = False
  nodaemon        = False

  # [modinit]
  # code = /usr/sbin/modprobe lirc_serial
  # code1 = /usr/bin/setfacl -m g:lirc:rw /dev/uinput
  # code2 = ...


  # [lircd-uinput]
  # add-release-events = False
  # release-timeout    = 200
  # release-suffix     = _EVUP
