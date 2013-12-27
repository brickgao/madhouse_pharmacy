# encoding: utf-8
from pickle import dumps, loads
import uuid
from struct import pack, unpack
import time
from decimal import Decimal, getcontext
from misc import create_counter


debug = True

getcontext().prec = 2
init_balance = Decimal('100000.00')
pickle_init_balance = dumps(init_balance, -1)

show, inc = create_counter(32)

spec = {'transaction step': ((show(), inc(1)), False, False,
                             lambda: pack('!B', 0),
                             lambda buf: int(unpack('!B', buf)[0])),
        'uid': ((show(), inc(16)), True, False,
                lambda: uuid.uuid4().bytes if not debug else uuid.UUID(hex='12345678' * 4).bytes,
                lambda buf: uuid.UUID(bytes=buf.value).bytes),
        'creation time': ((show(), inc(4)), True, False,
                          lambda: pack('!I', int(time.time())),
                          lambda buf: unpack('!I', buf)[0]),
        'expire time': ((show(), inc(4)), True, False,
                        lambda: pack('!I', int(time.mktime(time.strptime('2020 1 1', '%Y %m %d')))),
                        lambda buf: unpack('!I', buf)[0]),
        'last used time': ((show(), inc(4)), True, True,
                           lambda: pack('!I', int(time.time())),
                           lambda buf: unpack('!I', buf)[0]),
        'used time': ((show(), inc(4)), True, True,
                      lambda: pack('!I', 0),
                      lambda buf: unpack('!I', buf)[0]),
        'length of balance': ((show(), inc(4)), True, True,
                              lambda: pack('!I', len(pickle_init_balance)),
                              lambda buf: unpack('!I', buf)[0]),
        'balance': ((show(), inc(len(pickle_init_balance))), True, True,
                    lambda: pickle_init_balance,
                    lambda buf: loads(buf)),
        # hash: 32 bytes sha-256
        # backup: compressed backup data
}

next_offset = show()

spec = sorted(spec.iteritems(), key=lambda (_, ((offset, __), ___, ____, _____, ______)): offset)

