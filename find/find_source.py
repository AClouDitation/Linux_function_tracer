import os
import re
from statistics import mean, median

# find function definition
# @name: function name
# @path: function source C file path
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
					'(?:struct\s+|)\w+' +\
					# data type
					'(?:__sched\s+|)' +\
					#__sched?
					'(?:\*\s+|\s+\*|\s+)' +\
					# is pointer
					name +\
					# function name 
					'\s*\([^\)]*?\)\s*' +\
					# arguments and ()
					'(?:__releases\([^\)]*\)\s*|)' +\
					'(?:__acquires\([^\)]*\)\s*|)' +\
					'(?:__releases\([^\)]*\)\s*|)' +\
					# attributes
					'{', source_code)
		if m is not None:
			#print('found!')
			start = m.end()
			now = start
			stack = 1
			while stack > 0:
				now += 1
				if now == len(source_code):
					print('error!')
					break
				if source_code[now] == '{': stack += 1
				if source_code[now] == '}': stack -= 1
			return source_code[start:now + 1]
		else:
			print('cannot find %s in %s'%(name,path))
	else:
		print('error while opening source file')
	return None

# count lines of code
# @code: code text
def countline(code):

	lines = code.split('\n')
	for line in lines:
		if line.strip() == '':
			lines.remove(line)
	return len(lines)

