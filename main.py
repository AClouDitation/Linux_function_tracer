#!/usr/bin/env python3
import os
import re
from find.find_util import pre_process, traversalDir_FirstDir,\
					  	   gen_entry_list, fprint_list
from find.find_func import gen_call_tree, print_call_tree

# DESIRED ENTRY FUNCTION RULE
RULE = "[^\s]+(?:suspend|resume)"

# DIRS
VER = "4.4-rc6"

## substitute with your own pathes
KERNEL_PATH = os.path.join("/home/yq/Git/Linux_Kernel_ABI_Tracker/kernel","/linux-" + VER)
BUILD_PATH 	= os.path.join(KERNEL_PATH,"build/")
DRIVER_PATH = os.path.join(KERNEL_PATH,"build/drivers/")
OUTPUT_PATH = "./data_" + VER + "/"

# process global functions
global_dict = pre_process(BUILD_PATH, OUTPUT_PATH, KERNEL_PATH)

function_dict = {}
for d in traversalDir_FirstDir(DRIVER_PATH):
	path = os.path.join(OUTPUT_PATH, d)
	# If already fully searched, skip this
	if os.path.exists(os.path.join(path,"done.txt")):
		continue

	# Create dir if not exist
	if not os.path.exists(path):
		os.mkdir(path)

	# Generate entry dictionary
	entry_dict = gen_entry_list(
		os.path.join(DRIVER_PATH,d),
		global_dict, path, KERNEL_PATH,
		RULE)

	for key in entry_dict:
			entry_dict[key].attr += ' entry'

	# Generate call tree and print it!
	called_list = []
	with open(os.path.join(path,d+"_call_tree.txt"),"w") as f:
		for key in entry_dict:
			gen_call_tree(entry_dict[key], function_dict, global_dict, 0)
			print('______________________________________',file=f)
			print('entry function:\n%s: %s'%(key, entry_dict[key].attr),file=f)
			visited = []
			print_call_tree(entry_dict[key], 0, f, visited)
			print('______________________________________',file=f)
			# collect all visited functions
			called_list += visited
	# remove duplicated ones
	called_list = list(set(called_list))
	fprint_list(called_list, os.path.join(path, d+"_func_list.txt"))
	# Create done.txt indicate the folder is fully searched
	fp = open(os.path.join(path,"done.txt"),"w")
	fp.close()

# combine all function list
funclist = set()

for roots,dirs,files in os.walk(OUTPUT_PATH):
	for f in files:
		if re.match('^\w+_func_list.txt$',f):
			path = os.path.join(roots,f)
			with open(path,'r') as fp:
				for line in fp:
					func, path = line.strip().split(' ')
					funclist.add((func,path))			

with open('funclist.txt', 'w') as fp:
	for func in funclist:
		print(func[0],func[1], file=fp)
	
