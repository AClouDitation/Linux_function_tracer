#!/usr/bin/env python3
import os
import io
import sys
import re
from find.find_util import pre_process
import find.find_func as ff
import find.find_source as fs
from statistics import median

# OVERIDE FIND CONSTANTS
VER = "4.4-rc6"
KERNEL_PATH = "/home/yq/Git/Linux_Kernel_ABI_Tracker/kernel/linux-" + VER
BUILD_PATH 	= os.path.join(KERNEL_PATH,"build/")
DRIVER_PATH = os.path.join(KERNEL_PATH,"build/drivers/")
OUTPUT_PATH = "./data_" + VER + "/"

def o2c(path):
	p1,p2 = path.split('build/')
	path = p1 + p2
	path = path[:-1] + 'c'
	return path

# argvs:
# $1:	function name
# $2:	object file path
# $3:	path name filter, if there is $3, 
# 		only functions with path including $3 keyword is counted
if __name__ == '__main__':

	global_dict = pre_process(BUILD_PATH, OUTPUT_PATH, KERNEL_PATH)

	if len(sys.argv) != 3 and len(sys.argv) != 4:
		exit()
	name = sys.argv[1]
	path = sys.argv[2]

	target = ff.Func(name,path,None,None)
	func_dict = {}
	ff.gen_call_tree(target, func_dict, global_dict, 0)

	ls = [target]
	visited = set()
	fl = []
	while ls != []:
		now = ls[0]
		ls.pop(0)

		if now.name in visited:
			continue
		visited.add(now.name)
		fl.append((now.name, now.path))
		for c in now.call:
			ls.append(now.call[c])

	cnt = 0
	for x in fl:
		if x[1] is None:
			continue
		path = o2c(x[1])
		if not os.path.exists(path):
			continue
		sc = fs.find_source(x[0], path)	
		if sc is None: continue
		if len(sys.argv) == 4:
			if sys.argv[3] not in x[1]:
				continue
		ln = fs.countline(sc)
		cnt += ln
		print("%-40s:%60s:%d"%(x[0],x[1],ln))
	
	print('-----------------')
	print(cnt)

		

