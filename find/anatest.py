from statistics import mean, median
import os
import sys

if len(sys.argv) != 4:
	exit()
VER = sys.argv[1]
VER1 = sys.argv[2]
VER2 = sys.argv[3]

FN = 'change_list_'+VER1+'_to_'+VER2+'.txt'
FP = './change_lists/'

ks = []
kl = []
dl = []
ds = []
exp = set()
cl = set()

if VER == '4.4-rc6' or VER == '4.4-rc6-allyes':
	VERs = '4.4'
else:
	VERs = VER.split('.')
	VERs = VERs[0] + '.' + VERs[1]

with open('./change_lists/' + VERs + '_symbols.txt') as fp:
	for line in fp:
		exp.add(line.strip())

with open(os.path.join(FP,FN)) as fp:
	for line in fp:
		if line.count('|') != 1: continue
		name,_ = line.split('|')
		name = name.strip()
		if name in exp:
			cl.add(name)
	
with open(os.path.join('data_' + VER,'test.txt'), 'r') as fp:
	for line in fp:
		if line[:2] == '##': continue
		if line.count(':') != 2: continue

		name, path, ln = line.split(':')
		name = name.strip()

		path = path.strip()
		ln = int(ln.strip())

		if name not in cl: continue
		if ln == -1: continue

		if line[0] == '\t':
			if line[1] == '\t':
				ds.append(ln)
			else:
				dl.append(ln)
		else:
			if 'lib/' in path:	
				kl.append(ln)
			else:
				ks.append(ln)

if ks != []:
	print('--------kernel lib/services---------')
	print("MEAN:\t%d"%(mean(ks)))
	print("MEDIAN:\t%d"%(median(ks)))
	print("KL/KS:\t%d/%d"%(len(kl),len(ks)))
	print("TOTLEN:\t%d"%(sum(ks)))

if dl != []:
	print('--------driver libraries--------')
	print("MEAN:\t%d"%(mean(dl)))
	print("MEDIAN:\t%d"%(median(dl)))
	print("FIND/TOT:\t%d"%(len(dl)))
	print("TOTLEN:\t%d"%(sum(dl)))

if ds != []:
	print('--------device specific---------')
	print("MEAN:\t%d"%(mean(ds)))
	print("MEDIAN:\t%d"%(median(ds)))
	print("FIND/TOT:\t%d"%(len(ds)))
	print("TOTLEN:\t%d"%(sum(ds)))

print('------error and not found-------')
print("%d"%(len(cl) - len(ks) - len(ds) - len(dl)))


