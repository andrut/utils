#!/usr/bin/env python

import os, sys, time, getopt

class Color:
	DEFAULT = "\033[1;m"
	FILE = "\033[1;m" 
	FILEX = "\033[1;32m" 
	DIR = "\033[1;34m"
	SEPARATOR = "\033[1;35m" 
	START_TIME = "\033[1;36m"
	END_TIME = "\033[1;36m"

if not sys.stdout.isatty():
	Color.DEFAULT = Color.FILE = Color.FILEX = Color.DIR = Color.SEPARATOR = Color.START_TIME = Color.END_TIME = ""

def print_datetime(t):
	print "%s%s " % (Color.START_TIME, time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))),

def print_datetime_endl(t, st):
	if t - st > 3600*18:
		print "%s <=%s\n" % (Color.END_TIME, time.strftime("%Y-%m-%d %H:%M", time.gmtime(t)))
	elif t - st != 0:
		print "%s <=%s\n" % (Color.END_TIME, time.strftime("%H:%M", time.gmtime(t)))
	else:
		print ""

args, free_args = getopt.gnu_getopt(sys.argv[1:], '?d:h:sSY:D:H:')

time_span = 3600*24*7
older_than = 0
opt_absolute_span = True
now = time.time()

for arg in args:
	if arg[0] == '-d':
		time_span = 3600*24*float(arg[1])
	elif arg[0] == '-h':
		time_span = 3600*float(arg[1])
	elif arg[0] == '-s':
		opt_absolute_span = False
	elif arg[0] == '-S':
		opt_absolute_span = True
	elif arg[0] == '-Y':
		older_than = 3600*24*365*float(arg[1])
	elif arg[0] == '-D':
		older_than = 3600*24*float(arg[1])
	elif arg[0] == '-H':
		older_than = 3600*float(arg[1])
	elif arg[0] == '-?':
		print """Usage: %s [ARGS]
Args:
 -?      -- This help message
 -s      -- Group time span calculated file to file
 -S      -- Group time span calculated from first to last file [default]
 -h NUM  -- Group files by NUM hours span
 -d NUM  -- Group files by NUM days span
 -H NUM  -- Show files older than NUM hours
 -D NUM  -- Show files older than NUM days
 -Y NUM  -- Show files older than NUM years

 NUM may be a float number.""" % sys.argv[0]
 		sys.exit(0);

fns = os.listdir(".")
fns = filter(lambda f: f[0] != '.', fns)
fstats = map(lambda f: (f, os.stat(f)), fns)
fstats = sorted(fstats, key=lambda f: f[1].st_mtime)
if older_than:
	if older_than > 0:
		fstats = filter(lambda f: f[1].st_mtime <= now - older_than, fstats)
	else:
		fstats = filter(lambda f: f[1].st_mtime >= now + older_than, fstats)

last_mtime = 0
start_mtime = 0
first = True

if len(fstats) == 0:
	sys.exit(0)

for f in fstats:
	t = f[1].st_mtime
	if opt_absolute_span:
		rel_time = start_mtime
	else:
		rel_time = last_mtime
	if t - rel_time > time_span:
		if not first:
			print_datetime_endl(last_mtime, start_mtime)
		start_mtime = t
		print_datetime(t)
	else:
		sys.stdout.write(Color.SEPARATOR+" | ")
	if os.path.isdir(f[0]):
		sys.stdout.write(Color.DIR+f[0])
	elif f[1].st_mode & 0111 != 0:
		sys.stdout.write(Color.FILEX+f[0])
	else:
		sys.stdout.write(Color.FILE+f[0])
	last_mtime = t
	first = False
print_datetime_endl(last_mtime, start_mtime)
sys.stdout.write(Color.DEFAULT)
