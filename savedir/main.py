#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Andrzej Rutkowski
#
# --------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <andrzej.rutkowski@gmail.com> wrote this file. As long as you retain this 
# notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# - Andrzej Rutkowski
# --------------------------------------------------------------------------
#

import sys, os, time, getopt
try:
	import sqlite3 as sqlite
except ImportError:
	from pysqlite2 import dbapi2 as sqlite  # NOTTESTED

def dbClose():
	global db
	if db:
		db.commit()
		db.close()

db = None
configPath = os.path.expanduser("~/.savedir")
if not os.path.exists(configPath):
	try:
		os.mkdir(configPath)
	except OSError:
		exit(-1)
elif not os.path.isdir(configPath):
	exit(-1)
dbPath = configPath + "/dirs.sqlite"

if not os.path.exists(dbPath):
	installDB = True
else:
	installDB = False

db = sqlite.connect(dbPath);

if installDB:
	db.executescript("""	
		CREATE TABLE IF NOT EXISTS dirs (
			id INTEGER PRIMARY KEY,
			path TEXT,
			label TEXT,
			time INTEGER
			);
		CREATE INDEX IF NOT EXISTS dirslabel ON dirs (label);
		CREATE INDEX IF NOT EXISTS dirstime ON dirs (time);
	""");
	db.commit()

optClear = False
optClearLeave = 0
optListAll = False
optVerbose = False

recallMode = False
execName = os.path.basename(sys.argv[0])
if execName in ('memdir', 'lastdir'):
	recallMode = True

optLabel = None

args, argv = getopt.gnu_getopt(sys.argv[1:], 'l:Cc:avm', ['label=', 'clear-all', 'clear=', 'list-all', 'verbose', 'recall-mode']);

for arg in args:
	if arg[0] in ('-l', '--label'):
		optLabel = arg[1]
	elif arg[0] in ('-C', '--clear-all'):
		optClear = True
		if optLabel == None:
			optLabel = ''
		optClearLeave = 0
	elif arg[0] in ('-c', '--clear'):
		optClear = True
		try:
			optClearLeave = int(arg[1])
		except ValueError:
			print "Error: '%s' argument must be a number" % arg[0]
			dbClose()
			exit(-1)
	elif arg[0] in ('-a', '--list-all'):
		optListAll = True
	elif arg[0] in ('-v', '--verbose'):
		optVerbose = True
	elif arg[0] in ('-m', '--recall-mode'):
		recallMode = True

if not recallMode and optLabel == None:
	optLabel = ""

if optClear:
	if not recallMode:
		dbClose()
		exit(0)

	c = db.cursor()
	if optClearLeave <= 0:
		if optLabel == None:
			c.execute('delete from dirs')
		else:
			c.execute('delete from dirs where label = ?', (optLabel,))
	else:
		i = 0
		if optLabel == None:
			c.execute('select id from dirs order by id desc limit 1 offset ?', (optClearLeave - 1,))
		else:
			c.execute('select id from dirs where label = ? order by id desc limit 1 offset ?', (optLabel, optClearLeave - 1,))
		try:
			i = c.next()[0]
		except StopIteration:
			pass
		if optLabel == None:
			c.execute('delete from dirs where id < ?', (i,));
		else:
			c.execute('delete from dirs where label = ? and id < ?', (optLabel, i,));
	db.commit()
	dbClose()
	exit(0)

if recallMode:
	dirOffset = 0
	if len(argv) > 0:
		try:
			dirOffset = int(argv[0])
		except ValueError:
			optLabel = argv[0]

	c = db.cursor()
	if optLabel != None:
		if not optListAll:
			c.execute('select path, label from dirs where label=? order by id desc limit 1', (optLabel,))
		else:
			c.execute('select path, label from dirs where label=?', (optLabel,))
	else:
		c = db.cursor()
		if not optListAll:
			c.execute('select path, label from dirs order by id desc limit 1 offset ?', (dirOffset,))
		else:
			c.execute('select path, label from dirs')
	

	r = None
	while 1:
		try:
			r = c.next()
			if optVerbose:
				print "%s: %s" % (r[1], r[0])
			else:
				print r[0]
		except StopIteration:
			if r == None:
				print >> sys.stderr, "%s: No dirs found" % (execName,)
			break
		if not optListAll:
			break
else:
	c = db.cursor()
	if len(argv) == 0:
		c.execute('insert into dirs (path, label, time) values (?, ?, ?)', (os.getcwd(), optLabel, int(time.time())))
	else:
		for arg in argv:
			c.execute('insert into dirs (path, label, time) values (?, ?, ?)', (os.path.abspath(arg), optLabel, int(time.time())))

dbClose()
