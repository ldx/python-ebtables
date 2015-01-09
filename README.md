Ebtables
========

Ebtables is used for Ethernet bridge frame table administration on Linux. Python-ebtables is a simple Python binding for Ebtables.

If you are looking for `iptables` bindings, check [python-iptables](https://github.com/ldx/python-iptables).

Build
-----

You will need [CFFI](https://cffi.readthedocs.org/).

    $ python setup.py build
    [...]
    $ python setup.py install
    [...]

Check that you can import `ebtables`:

    $ python
    >>> import ebtables
    >>>

Usage
-----

Python-ebtables exposes an API that resembles the command line interface. For example:

    >>> import ebtables
    >>> rc, out, err = ebtables.nat('-L')
    >>> rc
    0
    >>> print out.split('\n')
    ['Bridge table: nat', '', 'Bridge chain: PREROUTING, entries: 0, policy: ACCEPT', '', 'Bridge chain: OUTPUT, entries: 0, policy: ACCEPT', '', 'Bridge chain: POSTROUTING, entries: 0, policy: ACCEPT', '']
    >>> err
    ''

Ebtables needs administrator privileges. However, if you don't want to run your python app as root, you only need the `CAP_NET_RAW` capability. For example:

    $ sudo PATH=$PATH capsh --caps="cap_net_raw+p" -- -c "python"
    [sudo] password for user:
    Python 2.7.9 (default, Dec 11 2014, 08:58:12)
    [GCC 4.9.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import ebtables
    >>> ebtables.filter('-L')
    (0, 'Bridge table: filter\n\nBridge chain: INPUT, entries: 0, policy: ACCEPT\n\nBridge chain: FORWARD, entries: 0, policy: ACCEPT\n\nBridge chain: OUTPUT, entries: 0, policy: ACCEPT\n', '')
    >>>
