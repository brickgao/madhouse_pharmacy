# encoding: utf-8

# WARNING
# Use Python of 32bit version please.
#

# setup log
from StringIO import StringIO
from functools import partial
import hashlib
import logging as log
import zlib
import card
from misc import create_counter

log.basicConfig(level=log.DEBUG)


from ctypes import *


___ = WinDLL('mwic_32.dll')

def make_conn():
    # is raw python int ok?
    dev = ___.ic_init(c_int(0), c_int(9600))
    if dev < 0:
        log.error('device not initialized')
        return False, 0

    # turn on device
    err = ___.turn_on(dev)
    if err:
        log.error('cannot turn card on')
        return False, 0

    # get status and check if card is in device
    card = c_int(0)
    err = ___.get_status(dev, byref(card))

    if err >= 0:
        log.info('device ok')
        if card:
            log.info('card in device')
        else:
            log.warning('no card')
            return False, 0
    else:
        log.error('device not ok')
        return False, 0

    # check if card is 4442
    err = ___.chk_4442(dev)
    if err:
        log.error('card not 4442')
        return False, 0

    # how to check card publishing?
    # how to read publisher

    return True, dev


def check_password(dev):
    counter = c_int(0)
    err = ___.rsct_4442(dev, byref(counter))

    if err >= 0:
        if not counter:
            log.error('card broken')
        else:
            log.info('password counter: %s', counter)

            # check user password
            user_pwd_bytes = raw_input('password? ').strip().decode('hex')

            # if this does not work, try (c_ubyte * 3)(*(unpack('=BBB', p)))
            err = ___.csc_4442(dev, 3,
                               create_string_buffer(user_pwd_bytes))
            if err >= 0:
                log.info('password matches')
                return True
            else:
                log.error('password does not match')

    return False


def write_with_counter(byte_counter, alt_stream, dev, offset, data):
    length = len(data)

    alt_stream.write(data)

    err = ___.swr_4442(dev,
                       offset,
                       length,
                       create_string_buffer(data))
    if not err:
        byte_counter(length)

    next_offset = offset + length

    return err, next_offset


def publish_card(dev):
    # initialize byte counter
    err = ___.swr_4442(dev,
                       32,
                       256 - 32,
                       create_string_buffer('\xff' * (256 - 32)))
    if err:
        log.error('error formatting card')

    counter, inc = create_counter()
    dummy_stream = StringIO()
    write = partial(write_with_counter, inc, dummy_stream)

    for name, ((offset, length), init_func, _) in card.spec:
        init = init_func()

        err, next_offset = write(dev, offset, init)
        if not err:
            log.info('wrote %s (offset %s, %s bytes): %s',
                     name,
                     offset,
                     length,
                     init.encode('hex'))
        else:
            log.error('error writing %s', name)
            return False

    next_offset = card.next_offset
    hash_obj = hashlib.sha1()
    hash_obj.update(dummy_stream.getvalue() + 'hash salt')
    err, next_offset = write(dev, next_offset, hash_obj.digest())
    if not err:
        log.info('wrote %s (offset %s, %s bytes): %s',
                 'hash',
                 next_offset - hash_obj.digest_size,
                 hash_obj.digest_size,
                 hash_obj.digest().encode('hex'))

    compressed = zlib.compress(dummy_stream.getvalue(), 9)
    err, next_offset = write(dev, next_offset, compressed)
    if not err:
        log.info('wrote %s (offset %s, %s bytes): %s',
                 'backup',
                 next_offset - len(compressed),
                 len(compressed),
                 compressed.encode('hex'))

    log.info('wrote %s bytes in total', counter())
    return True


def check_manufacture(dev):
    manufacture = create_string_buffer(9)
    err = ___.srd_4442(dev, 0, 8, manufacture)
    if not err:
        if manufacture.value == 'madhouse':
            return True
    return False


def transact_read_info(dev):
    card_dict = {}
    if check_manufacture(dev):
        # do transaction
        for name, ((offset, size), _, gen_func) in card.spec:
            buf = create_string_buffer(size) # size + 1? test needed
            err = ___.srd_4442(dev, offset, size, buf)
            if not err:
                card_dict[name] = gen_func(buf)
    return card_dict



if __name__ == '__main__':
    conn, dev = make_conn()

    pwd_checked = False
    if conn:
        pwd_checked = check_password(dev)

    if pwd_checked:
        publish_card(dev)



