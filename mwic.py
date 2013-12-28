# encoding: utf-8

# WARNING
# Use Python of 32bit version please.
#

# setup log
from StringIO import StringIO
from decimal import *
from functools import partial
import hashlib
import logging as log
import pickle
import struct
import zlib
import time
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


def check_password(dev, password):
    counter = c_int(0)
    err = ___.rsct_4442(dev, byref(counter))

    if err >= 0:
        if not counter:
            log.error('card broken')
        else:
            if counter < 2:
                log.warning('password counter: 1, card be banned')
                return False

            log.info('password counter: %s', counter)

            # check user password
            user_pwd_bytes = password.decode('hex')

            # if this does not work, try (c_ubyte * 3)(*(unpack('=BBB', p)))
            err = ___.csc_4442(dev, 3,
                               create_string_buffer(user_pwd_bytes))
            if err >= 0:
                log.info('password matches')
                return True
            else:
                log.error('password does not match')

    return False


def write_with_counter(byte_counter, alt_stream, dev, offset, data, write_to_alt):
    length = len(data)

    if write_to_alt:
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
    card_format = {}
    for name, ((offset, length), _, _, put, _) in card.spec:
        card_format[name] = put()

    write_card(dev, card_format)


def write_card(dev, card_dict):
    # initialize byte counter
    err = ___.swr_4442(dev,
                       32,
                       256 - 32,
                       create_string_buffer('\xff' * (256 - 32)))
    if err:
        log.error('error formatting card')

    counter, inc = create_counter()
    dummy_stream = StringIO()
    write = partial(write_with_counter, inc, dummy_stream, dev)
    transact_step = 0
    next_offset = -1
    for name, ((offset, length), shall_hash, is_transact, _, _) in card.spec:
        val = card_dict[name]

        err, next_offset = write(offset, val, shall_hash)
        if not err:
            log.info('wrote %s (offset %s, %s bytes, hash %s): %s',
                     name,
                     offset,
                     length,
                     shall_hash,
                     val.encode('hex'))
            if is_transact:
                transact_step = (transact_step + 1) % 7
        else:
            log.error('error writing %s', name)
            return False

    assert next_offset > 0

    hash_obj = hashlib.sha1()
    hash_obj.update(dummy_stream.getvalue() + 'hash salt')
    err, next_offset = write(next_offset, hash_obj.digest(), True)
    if not err:
        log.info('wrote %s (offset %s, %s bytes): %s',
                 'hash',
                 next_offset - hash_obj.digest_size,
                 hash_obj.digest_size,
                 hash_obj.digest().encode('hex'))
        transact_step = (transact_step + 1) % 7
    else:
        log.error('error writing hash')
        return False

    compressed = zlib.compress(dummy_stream.getvalue(), 9)
    len_of_compressed = len(compressed)
    err, next_offset = write(next_offset,
                             struct.pack('!I', len_of_compressed), False)
    if not err:
        log.info('wrote %s (offset %s, %s bytes): %s',
                 'len of backup',
                 next_offset - 4,
                 4,
                 struct.pack('!I', len_of_compressed).encode('hex'))
        transact_step = (transact_step + 1) % 7
    else:
        log.error('error writing length of backup')
        return False

    err, next_offset = write(next_offset, compressed, False)
    if not err:
        log.info('wrote %s (offset %s, %s bytes): %s',
                 'backup',
                 next_offset - len(compressed),
                 len(compressed),
                 compressed.encode('hex'))
        transact_step = (transact_step + 1) % 7
    else:
        log.error('error writing backup')
        return False

    err = ___.swr_4442(dev, 32, 1,
                       create_string_buffer(struct.pack('!B', transact_step)))
    if not err:
        if not transact_step:
            log.info('transaction completed successfully')
        else:
            log.warning('transaction incomplete')
    else:
        log.error('error writing transaction step')
        return False


    log.info('wrote %s bytes in total', counter())
    return True


def ready(dev):
    hash_io = StringIO()
    d = {}
    for name, ((offset, length), shall_hash, _, _, get) in card.spec[:-1]:
        buf = create_string_buffer(length)

        err = ___.srd_4442(dev, offset, length, buf)
        if err:
            log.error('error reading %s', name)
            return False

        if shall_hash:
            hash_io.write(buf.raw)
        d[name] = get(buf)
        log.info('read %s: %s, hash %s', name, d[name], shall_hash)

    len_of_balance = d['length of balance']
    key, ((offset, _), _, _, _, get) = card.spec[-1]
    buf = create_string_buffer(len_of_balance)

    err = ___.srd_4442(dev, offset, len_of_balance, buf)
    if err:
        log.error('error reading balance')
        return False
    hash_io.write(buf.raw)
    d[key] = get(buf)

    hash_offset = offset + len_of_balance
    hash_buf = create_string_buffer(20)
    err = ___.srd_4442(dev, hash_offset, 20, hash_buf)
    if err:
        log.error('error reading hash')
        return False
    d['hash'] = hash_buf.raw

    lob_offset = hash_offset + 20
    lob_buf = create_string_buffer(4)
    err = ___.srd_4442(dev, lob_offset, 4, lob_buf)
    if err:
        log.error('error reading length of backup')
    len_of_backup = struct.unpack('!I', lob_buf)[0]
    d['length of backup'] = len_of_backup

    backup_offset = lob_offset + 4
    backup_buf = create_string_buffer(len_of_backup)
    err = ___.srd_4442(dev, backup_offset, len_of_backup, backup_buf)
    if err:
        log.error('error reading backup')
    backup = zlib.decompress(backup_buf.raw)
    d['backup'] = backup

    hash_obj = hashlib.sha1()
    hash_obj.update(hash_io.getvalue() + 'hash salt')

    if hash_obj.digest() != hash_buf.value:
        log.warning('hash not match: %s, %s',
                    hash_obj.hexdigest(),
                    hash_buf.value.encode('hex'))
        return d['backup']
    if d['transaction step'] != 0:
        return d['backup']

    return d


def restore_from_backup(dev, backup):
    err = ___.swr_4442(dev, 33, len(backup), create_string_buffer(backup))
    if err:
        log.error('restoration failed')


def modify_balance(dev, card_dict, how_much):
    card_dict = card_dict.copy()

    balance = card_dict['balance']
    balance = Decimal('%.2f' %
                      ((int(balance * 100) -
                        int(Decimal(how_much) * 100)) / 100.))

    card_dict['balance'] = pickle.dumps(balance, protocol=-1)
    card_dict['length of balance'] = len(card_dict['balance'])
    card_dict['last used time'] = time.time()
    card_dict['used time'] += 1

    pack_dict(card_dict)
    return write_card(dev, card_dict)


def pack_dict(d):
    for name, fmt in [('transaction step', '!B'),
                      ('creation time', '!I'),
                      ('expire time', '!I'),
                      ('last used time', '!I'),
                      ('used time', '!I'),
                      ('length of balance', '!I')]:
        d[name] = struct.pack(fmt, d[name])


if __name__ == '__main__':
    conn, dev = make_conn()

    pwd_checked = False
    if conn:
        pwd_checked = check_password(dev, 'ffffff')

    if pwd_checked:
        publish_card(dev)
    this_card = ready(dev)
    if isinstance(this_card, bool):
        if not this_card:
            print 'fuck'
    elif isinstance(this_card, basestring):
        print 'card failed, trying to restore from backup'
        restore_from_backup(dev, this_card)
    elif isinstance(this_card, dict):
        print this_card
        modify_balance(dev, this_card, '300.00')
        print this_card

    this_card = ready(dev)
    print this_card



