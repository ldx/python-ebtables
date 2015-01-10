import fcntl
import os
import sys
from cffi import FFI

__version__ = '0.1.0-dev'

EBTABLES_LIBRARY_PATH = os.getenv('EBTABLES_LIBRARY_PATH') or '/lib/ebtables'


class EbtablesException(Exception):
    pass


def _get_libname(f):
    prefix = f.find('lib')
    if prefix != -1:
        f = f[prefix + 3:]
    if f.endswith('.so'):
        f = f[:-3]
    return f


def _get_libraries():
    files = os.listdir(EBTABLES_LIBRARY_PATH)
    return [_get_libname(f) for f in files if f.endswith('.so')]


ffi = FFI()

ffi.cdef(
    """
    #define EBT_TABLE_MAXNAMELEN 32

    #define ERRORMSG_MAXLEN 128

    #define EXEC_STYLE_PRG ...
    #define EXEC_STYLE_DAEMON ...

    struct ebt_u_replace {
        char name[EBT_TABLE_MAXNAMELEN];
        ...;
    };

    extern char ebt_errormsg[ERRORMSG_MAXLEN];

    extern int ebt_silent;

    extern char *optarg;
    extern int optind;

    int do_command(int argc, char *argv[], int exec_style,
    struct ebt_u_replace *replace_);
    int ebt_get_kernel_table(struct ebt_u_replace *replace, int init);
    void ebt_early_init_once(void);
    void ebt_deliver_table(struct ebt_u_replace *u_repl);

    char *strcpy(char *dest, const char *src);
    """)

_ebtc = ffi.verify(
    """
    #include <stdio.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include "include/ebtables.h"
    #include "include/ebtables_u.h"

    extern char ebt_errormsg[ERRORMSG_MAXLEN];

    extern int ebt_silent;

    extern char *optarg;
    extern int optind;

    void ebt_early_init_once(void);
    """,
    libraries=_get_libraries(),
    include_dirs=[os.path.dirname(os.path.abspath(__file__))],
    library_dirs=[EBTABLES_LIBRARY_PATH],
    runtime_library_dirs=[EBTABLES_LIBRARY_PATH],
    modulename='ebtables_cffi')

_ebtc.ebt_silent = 1
_ebtc.ebt_errormsg[0] = '\0'


def _get_errormsg():
    msg = ffi.string(_ebtc.ebt_errormsg)
    _ebtc.ebt_errormsg[0] = '\0'
    return msg

_tables = {}


def _populate_table(t):
    if not _tables:
        _ebtc.ebt_early_init_once()
    rpl = ffi.new('struct ebt_u_replace *')
    _ebtc.strcpy(rpl.name, ffi.new('char[]', t))
    if _ebtc.ebt_get_kernel_table(rpl, 0) != 0:
        raise EbtablesException('ebt_get_kernel_table() failed %s' %
                                _get_errormsg())
    _tables[t] = rpl  # ffi.new('struct ebt_u_replace *')


def _populate_tables():
    for t in ['filter', 'nat', 'broute']:
        _populate_table(t)


def _do_command(rpl, args):
    _get_errormsg()
    rc = _ebtc.do_command(len(args), args, _ebtc.EXEC_STYLE_DAEMON, rpl)
    err = _get_errormsg()
    if rc == 0 and not err:
        _ebtc.ebt_deliver_table(rpl)
        err = _get_errormsg()
        if err:
            rc = -1
            err = 'ebt_deliver_table() failed %s' % err
        # _ebtc.ebt_cleanup_replace(rpl)
    return rc, err


def _cmd(rpl, args):
    sys.stdout.flush()
    stdout = os.dup(1)
    pipes = (None, None)
    cmd_out = ''
    cmd_err = ''
    try:
        pipes = os.pipe()
        fcntl.fcntl(pipes[0], fcntl.F_SETFL, os.O_NONBLOCK)
        os.dup2(pipes[1], 1)

        rc, cmd_err = _do_command(rpl, args)

        tmp_out = []
        while True:
            try:
                buf = os.read(pipes[0], 1024)
            except OSError as e:
                if e.errno == 11:
                    break
                else:
                    raise
            if not buf:
                break
            tmp_out.append(buf)
        cmd_out = ''.join(tmp_out)
        return rc, cmd_out, cmd_err
    except:
        return -1, cmd_out, cmd_err
    finally:
        for p in pipes:
            if p is not None:
                os.close(p)
        os.dup2(stdout, 1)
        os.close(stdout)


def cmd(table, params):
    if isinstance(params, str):
        params = params.split()

    _ebtc.optarg = ffi.NULL
    _ebtc.optind = 0

    args_list = [ffi.new('char []', './ebtables')]
    for p in params:
        args_list.append(ffi.new('char []', p))
    args = ffi.new('char *[]', args_list)

    if table not in _tables:
        _populate_table(table)
    rpl = _tables[table]
    # _ebtc.strcpy(rpl.name, ffi.new('char[]', table))

    return _cmd(rpl, args)


def filter(params):
    return cmd('filter', params)


def nat(params):
    return cmd('nat', params)


def broute(params):
    return cmd('broute', params)
