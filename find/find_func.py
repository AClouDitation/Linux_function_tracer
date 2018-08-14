import os
import sys
import re

# Constants
FUNC_GENERAL_RULE = re.compile("[\da-f]{8}\s<[^+\n]+>:")
MAX_SEARCHING_DEPTH = 100


done = []

class Func(object):
	
	# Func constructor 
	# @name: function name
	# @path: object file path
	# @symtable: symtable text
	# @dump:	 dump text
	def __init__(self, name, path, symtable, dump):
		self.name 		= name	# function name
		self.path 		= path	# function object file path
		self.call 		= {}	# functions called by this function
		self.ascode 	= None	# assymbly code 
		self.dump 		= None	# object file dump text
		self.symtable 	= None	# symbol table
		self.visited 	= False	# visited or not
		self.attr 		= ''	# attributions

		# If already known, store it
		if dump is not None and symtable is not None:
			self.symtable	= symtable
			self.dump 		= dump

		# Get the assymbly code of this function
		if self.dump is not None:
			self.ascode 	= self.__find_func_ascode()


	# Slice the assymbly code of this function from the entire dump file
	def __find_func_ascode(self):
		
		# Find the assymbly code with RE
		func_dec = re.compile(func_dec_rule(self.name))
		match = func_dec.search(self.dump)

		# If not exist, raise error
		if match == None:
			#TODO: raise error, can be done later
			return None
		# Find next function assymbly code header location
		nxmatch = FUNC_GENERAL_RULE.search(self.dump[match.end()::])
		# If this is the last function in the dumped file
		if nxmatch == None:
			return self.dump[match.end()::]
		# Or not
		else:
			return self.dump[match.end():match.end() + nxmatch.start()].strip('\n')


	# Find all function calls within the assymbly of this function
	# @fdic:	function dictionary
	# @gdic:	global function dictionary
	def __find_func_call(self, fdic, gdic):

		# Parse dumped codes and find function calls
		func_call = re.compile("\s+[\da-f ]{4}:\s+[\da-f]{8}\s+(\w+)\s+([^\n]+)")
		for x in func_call.finditer(self.ascode):
			# Instruction is branch?
			if x.group(1) == 'bl':
				#TODO: add support for blx??
				# Get name of called function
				call_name = re.match('^[^<]+<([^>]+)>$',x.group(2)).group(1)
				# If already processed, skip
				if call_name in self.call:
					continue

				# Search in global function list
				# global functions are pre-processed
				# append directly
				if call_name in gdic:
					self.call[call_name] = gdic[call_name]

				# Search in current object file 
				# if function is declared in the same file
				# append as local function
				elif re.search(func_dec_rule(call_name), self.dump) is not None:
					# If function is already processed
					if call_name in fdic:
						self.call[call_name] = fdic[call_name]
					# Or not
					else:
						# Create new Func object with same path, symtable, and dump
						call_func = Func(call_name, self.path, self.symtable, self.dump)
						fdic[call_name] = call_func
						self.call[call_name] = call_func
						self.call[call_name].attr += ' local'
				else:
					# function is out of scope or error has occured
					self.call[call_name] = Func(call_name, None, None, None)
					self.call[call_name].attr += ' unknown'


	# Pre-process before actual __find_func_call
	# @fdir: 	processed function dictionary
	# @gdic: 	global function dictionary
	def find_func_call(self, fdic, gdic):

		# If this function is out of our scope
		if self.path is None: return
		# If haven't dump yet, try to dump
		if self.dump is None:
			self.symtable, self.dump = objdump(self.path)
		# Find assymbly code if not processed yet
		if self.ascode is None and self.dump is not None:
			self.ascode = self.__find_func_ascode()
		# If cannot find assymbly code, raise error
		if self.ascode is None:
			#raise
			return

		#if (self.name, self.path) in done:
		#	return

		done.append((self.name, self.path))
		self.visited = True
		self.__find_func_call(fdic, gdic)


# Generate RE rule finding function codes header
# @name: target function name
def func_dec_rule(name):
	return "[\da-f]{8}\s<("+name+")>:"

# Find all global functions in kernel
# @path: build path
def find_global_func(path):
	func_dic = {}
	symtable, dump = objdump(path)
	if symtable is None or dump is None:
		return func_dic 

	symrule = re.compile("[\da-f]{8}\s([\s\S]{6}F)\s[^\s]+\s[\da-f]{8}\s([^\s]+)\n")

	# we assume global functions are unique
	name_ls = [x.group(2) for x in symrule.finditer(symtable) \
		if x.group(1)[0] == 'g' or x.group(1)[0] == 'u']
			
	for x in name_ls:
		func_dic[x] = Func(x, path, symtable, dump)
		
	return func_dic


# Find all entry functions in certain object file
# @path: target file path
# @gdic: global dictionary
def find_entry_func(path, gdic):

	func_dic = {}
	# Dump it!
	symtable, dump = objdump(path)

	# If failed to dump, return
	if symtable is None or dump is None:
		return func_dic 

	# RE rule for suspend/resume entry
	# 	general symbol tabel paser
	symrule	 	= re.compile("[\da-f]{8}\s([\s\S]{6}F)\s[^\s]+\s[\da-f]{8}\s([^\s]+)\n")
	#	determine line is desired entry
	entryrule 	= re.compile("[^\s]+(?:suspend|resume)")

	# Find all valid entry name
	name_ls = set([x.group(2) for x in symrule.finditer(symtable)\
		if entryrule.match(x.group(2))])

	for x in name_ls: 
		if x in gdic:
			func_dic[x] = gdic[x]
		else:
			func_dic[x] = Func(x, path, symtable, dump) 

	return func_dic

# Generate call tree!
# @func: target function
# @fdic: processed function dictionary
# @gdic: global function dictionary
# @depth: recursion depth
def gen_call_tree(func, fdic, gdic, depth):

	if depth > MAX_SEARCHING_DEPTH:	return
	if func.visited: return
	
	func.find_func_call(fdic, gdic)

	for f in func.call:
		gen_call_tree(func.call[f], fdic, gdic, depth + 1)


# call gen_call_tree before call this function
# otherwise print nothing
# @func: 	entry function
# @depth: 	recursion depth
# @fp: 		target file handler
# @visited: visited functions
def print_call_tree(func, depth, fp, visited):
	
	if re.search('global',func.attr): 
		e = (func.name, 'global')
	else:
		e = (func.name, func.path)
	if e in visited:
		print("%s"%('\t' + '│\t\t'*depth + '├━━━━━━'+'visited!'), file=fp)
		return

	visited.append(e)
	for f in func.call:
		print("%s: %s"%('\t' + '│\t\t'*depth + '├━━━━━━'+\
			func.call[f].name, func.call[f].attr), file=fp)
		print_call_tree(func.call[f], depth + 1, fp, visited)


# Dump object file
# @path: object file path
def objdump(path):
	
	if path[-2:] != ".o":
		print("error dumping file path:",path)
		return None, None
	dump_path, dump_name = os.path.split(path)
	dump_path = os.path.join(dump_path, dump_name[:-2] + '.dump')
	if not os.path.exists(dump_path):
		cmd = 'arm-linux-gnueabihf-objdump -D -t ' + path + ' > ' + dump_path
		os.system(cmd)
	f = open(dump_path,'r')
	if f is not None:
		dump = f.read()
		f.close()
		s1 = re.search("SYMBOL TABLE:",dump)
		s2 = re.search("Disassembly of section [^:]+:",dump)
		if s1 == None or s2 == None:
			print(path,file=sys.stderr)
			return None, None
		return dump[s1.end():s2.start()].strip()+'\n', dump[s2.end():].strip()+'\n'

	print("failed to dump file")
	return None, None

