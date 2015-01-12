import ebtables
import functools
import pytest
import random
import string


# A few basic rules to test in all three tables.
TEST_RULES = [
    '-p ARP -j ACCEPT',
    '-p IPv4 -j ACCEPT',
    '-p Length -j ACCEPT',
    '-p IPv4 -i eth0 --ip-dst 172.16.1.1 -j ACCEPT',
    '-p ARP -d 11:22:33:44:55:66 -o eth0 -j ACCEPT',
    '-p ARP -i eth0 --arp-ip-dst 172.16.1.1 -j ACCEPT',
    '-p IPv4 --log-level info --log-prefix FW --log-ip --log-arp -j ACCEPT',
    '-p 802_1Q --vlan-id 1 -j mark --mark-set 0x1 --mark-target ACCEPT']


@pytest.fixture(params=TEST_RULES)
def rule(request):
    return request.param


@pytest.fixture
def chain():
    rnd = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for _ in range(16))
    chain = 'test_chain_%s' % rnd
    return chain


@pytest.fixture(params=['filter', 'nat', 'broute'])
def table(request, chain):
    t = request.param
    cmd = functools.partial(ebtables.cmd, t)

    def remove():
        cmd('-F %s' % chain)
        cmd('-X %s' % chain)
    request.addfinalizer(remove)

    rc, out, err = cmd('-L %s' % chain)
    if rc == 0:
        cmd('-F %s' % chain)
        cmd('-X %s' % chain)
    rc, out, err = cmd('-N %s' % chain)
    assert rc == 0, "Error removing %s; out: %s; err: %s" % (chain, out, err)
    return cmd


def _test_add(table, chain, rule, cmd):
    rc, out, err = table('%s %s %s' % (cmd, chain, rule))
    assert rc == 0, "Error adding %s; out: %s; err: %s" % (rule, out, err)
    rc, out, err = table('-L %s' % chain)
    assert rc == 0, "Error listing %s; out: %s; err: %s" % (chain, out, err)
    for line in out.split('\n'):
        if line.strip().replace('"', '').startswith(rule):
            break
    else:
        assert 0, "Missing rule '%s'; output: %s" % (rule, out)
    rc, out, err = table('-D %s %s' % (chain, rule))
    assert rc == 0, "Error removing %s; out: %s; err: %s" % (rule, out, err)


#
# Test inserting and then removing a rule.
#
def test_insert(table, chain, rule):
    _test_add(table, chain, rule, '-I')


#
# Test appending and then removing a rule.
#
def test_append(table, chain, rule):
    _test_add(table, chain, rule, '-A')
