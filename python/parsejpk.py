#!/usr/bin/python
def mismatchstack(lscols):
	"""
	hstack for columns with different lengths. Columns are aligned at the top
	"""
	from numpy import concatenate, ones, nan, hstack
	clength = max([len(col) for col in lscols])
	longcols = [concatenate(c, NaN * ones((clength-len(c), 1))) for c in lscols]
	tableout =



def parsejpkfile(fname, col_heads = {'vDeflection':'d', 'smoothedCapacitiveSensorHeight':'z'}, constants = {'springConstant:':'kcant', 'sensitivity:':'sens'}):
	from numpy import array
	from os.path import basename
	fstruc = {value:[] for value in col_heads.values() + constants.values()}
	fstruc['filename'] = basename(fname)
	with open(fname) as f:
		rows = (row.strip().split(' ') for row in f if row.strip('#').strip()) # this generator object basically filters out empty lines and makes the others easier to process
		for r in rows:
			if r[0] == '#' and r[1] == 'columns:':
				cols = {col_heads[hdr]:r.index(hdr)-2 for hdr in col_heads.iterkeys()}
				for hdr in col_heads.itervalues():
					if not hdr in cols.keys():
						print('Missing' + hdr + ' column')
						return
			elif r[0] == '#' and any(r[1] == key for key in constants.keys()):
				fstruc[constants[r[1]]] = r[2]
			elif r[0] != '#':
				for hdr in cols.iterkeys():
					fstruc[hdr].append(float(r[cols[hdr]]))
	for hdr in col_heads.itervalues():
		fstruc[hdr] = array(fstruc[hdr])
		fstruc[hdr] = fstruc[hdr].reshape((-1,1))
	return fstruc

def selectdir(conffile = '.parsejpk_lastdir', indir = ''):
	from Tkinter import Tk	# ugly, but functional
	from tkFileDialog import askdirectory
	from os.path import isfile, dirname, abspath
	if isfile(conffile) and not indir:
		with open(conffile, 'r') as cf:
			indir  = cf.readline()
	Tk().withdraw()
	folder = askdirectory(initialdir = indir)
	with open(conffile, 'w') as cf:
		cf.write(dirname(abspath(folder)))
	return folder

def parsejpkdir(folder = ''):
	from os import listdir
	from os.path import isfile, join, isdir, split
	from numpy import hstack
	if not folder: folder = selectdir()
	f_ls = sorted([join(folder, f) for f in listdir(folder) if isfile(join(folder, f)) and f.endswith('.txt')])
	dirstruct = {'directory':folder, 'kcant':'', 'sens':'', 'curves':dict()}
	fcount = 0
	for f in f_ls:
		fcount +=1
		dirstruct['curves'][fcount] = parsejpkfile(f)
		for cntlprop in ['kcant','sens']:
			if not dirstruct[cntlprop]:
				dirstruct[cntlprop] = dirstruct['curves'][fcount][cntlprop]
			elif dirstruct['curves'][fcount][cntlprop] != dirstruct[cntlprop]:
				print('Cantilever characteristic ' + cntlprop + ' changes between files in folder ' + folder)
				return

	return dirstruct

def jpkcsv(folder = '', arg = 'n'):
	from os import listdir
	from os.path import isdir, join, abspath, pardir, basename
	from scipy.io import savemat
	from sys import stdout
	if not folder: folder = selectdir()
	print(folder)
	dirlist = sorted([join(folder, d) for d in listdir(folder) if isdir(join(folder, d))])
	toolbar_width = len(dirlist)
	stdout.write("[%s]" % (" " * toolbar_width))
	stdout.flush()
	stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
	notexped = []
	with open(join(folder, 'springConstantIndex.csv'), 'w') as kInd: kInd.write('filename, springConstant\n')
	for d in dirlist:
		if arg == 'v':
			stdout.write(basename(d)+'\n')
		else:
			stdout.write("|")
		stdout.flush()
		dstruct = parsejpkdir(d)
		if dstruct:
			savemat(join(abspath(join(d, pardir)), '.'.join([d,'mat'])), dstruct)
			with open(join(folder, 'springConstantIndex.csv'), 'a') as kInd: kInd.write(basename(d) + ', ' + str(dstruct['kcant'][0]) + '\n')
		else:
			notexped.append(basename(d))
	stdout.write("\n")
	if notexped:
		print('Folders not exported:')
		for f in notexped:
			print
	return None

if __name__ == "__main__":
	import sys

	if len(sys.argv) > 1:
		if sys.argv[1] == 'v':
			print('Verbose \n')
			jpkmat(folder = '', arg = 'v')
		else:
			jpkmat()
	else:
		jpkmat()
