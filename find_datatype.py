import os
import sys
import re
from statistics import mean, median

VER = sys.argv[1]
PATH = './data_' + VER

def find_source(name, path):
	source_code = None
	with open(path, 'r',encoding='ISO-8859-1') as fp:
		ln = 0
		source_code = fp.read()

	if source_code is not None:
		m = re.search('(?:static|)\s+' +\
					# static or not
					'(?:inline\s+|)' +\
					# inline or not
					'((?:struct\s+|)\w+)' +\
					# data type
					'(?:__sched\s+|)' +\
					#__sched?
					'(?:\*\s+|\s+\*|\s+)' +\
					# is pointer
					name +\
					# function name 
					'\s*\(([^\)]*?)\)\s*' +\
					# arguments and ()
					'(?:__releases\([^\)]*\)\s*|)' +\
					'(?:__acquires\([^\)]*\)\s*|)' +\
					'(?:__releases\([^\)]*\)\s*|)' +\
					# attributes
					'{', source_code)
		if m is not None:
			return m.group(1), m.group(2)
	return None, None


def countline(code):

	lines = code.split('\n')
	for line in lines:
		if line.strip() == '':
			lines.remove(line)
	return len(lines)


def b2s(bPath):
	try:
		kPath,dPath = bPath.split('/build')
	except:
		#print('error! ' + bPath)
		return None

	sPath = kPath + dPath
	sPath = sPath[:-1] + 'c'

	if os.path.exists(sPath):
		return sPath
	else:
		return None

ls = []
cnt = 0
entry_cnt = 0
gf_path = {}


with open(os.path.join(PATH, 'global_funclist.txt'), 'r') as fp:
	for line in fp:
		name, path = line.split(' ')
		name = name.strip()
		path = path.strip()
		gf_path[name] = path
		

with open(os.path.join(PATH, 'funclist.txt'), 'r') as fp:
	for line in fp:
		if line[0] == '-':
			continue
		else:
			name, path = line.split(' ')
			name = name.strip()
			path = path.strip()
			if path == 'None':
				continue
			if path == 'global':
				attr = 'global'
			else:
				attr = 'local'
			if path == 'global':
				path = gf_path[name]
			
			path = b2s(path)
			if path is not None:
				ls.append((name, path, attr))
	

ls = list(set(ls))
ls = sorted(ls, key = lambda x: (x[1],x[0]))

type_set = set()
for line in ls:
	rtype, ctype = find_source(line[0], line[1])
	if rtype == None or ctype == None: continue

	#print(rtype, ctype, line[1])
	typels = [x for x in ctype.split(',') if x.count('struct') != 0]
	#typels.append(rtype)
	for t in typels: 
		t = t.strip()
		tls = t.split()
		for i in range(len(tls)):
			if tls[i] == 'struct' and i + 1 < len(tls):
				type_set.add((tls[i+1], line[1]))

for t in type_set:
	print(t[0])


