import os
import sys
import re
from . import find_util as util

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
			self.symtable, self.dump = util.objdump(self.path)
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

