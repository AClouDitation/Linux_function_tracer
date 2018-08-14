#!/usr/bin/env python3
import os
import sys
import re


# CONSTANTS
VER = sys.argv[1]
KERNEL_PATH = '/home/yq/Git/Linux_Kernel_ABI_Tracker/kernel/linux-' + VER
OUTPUT_FN = VER.split('.')[0] + '.' + VER.split('.')[1] + '_export.txt'
cmd = 'grep --exclude=export.txt -rn -e \'EXPORT_SYMBOL\' ' + \
	KERNEL_PATH + ' > ' + OUTPUT_FN

print(cmd, file=sys.stderr)
os.system(cmd)
with open(OUTPUT_FN,'r') as fp:	
	for line in fp:

		if line.count(':') == 0:
			continue
	
		e = line.split(':')[-1].strip()
		m = re.match('^EXPORT_SYMBOL' +\
				 '(?:_GPL|)'+\
				 '\(([^\)]+)\);$',e)		
		if m is not None:
			print(m.group(1))

cmd = 'rm ' + OUTPUT_FN + ' -rf'
print(cmd, file=sys.stderr)
os.system(cmd)
