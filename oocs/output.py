# This python module is part of the oocs scanner for Linux.
# Copyright (C) 2015 Davide Madrisan <davide.madrisan.gmail.com>

# Simple output primitives

import errno, os, stat, sys

TABSTR = '   '

def colonize(message):
    #return ": %s" % message if message else ''
    if not message: return ''
    return ": %s" % message

def quote(message):
    return "'%s'" % message

def message(message, **options):
    dots = options.get('dots') and ' ...' or ''
    end = options.get('end') or '\n'
    tab = options.get('tab') or 0
    prefix = options.get('header') and '\n*** ' or ''

    sys.stdout.write(tab*TABSTR + prefix + str(message) + dots + end)

def message_abort(message):
    sys.exit('Fatal error: ' + message + ' - aborting...')

def message_alert(message, **options):
    extra_message = options.get('reason') or ''
    level = options.get('level') or 'warning'
    print(level.upper() + colonize(message) + colonize(extra_message))

def message_ok(message):
    print('OK: ' + message)
