#!/usr/bin/python
def parsejpkfile(fname, col_heads = ["vDeflection", "smoothedCapacitiveSensorHeight"]):
	from numpy import array
	csvrows, struct = [], {'springConstant:':[],'sensitivity:':[]}
	with open(fname) as f:
		snarfed = (row.strip().split(' ') for row in f if row.strip('#').strip())
		for row in snarfed:
			if row[1] == 'columns:':
				cols = {hdr:row.index(hdr)-2 for hdr in col_heads}
			elif row[0] == '#':
				if len(row) >= 3: struct[row[1]] = row[2] #catch any extra information in the file
			elif row[0] != '#':
				csvrows.append(row)
	for hdr in col_heads:
		if not hdr in cols.keys():
			print('Missing ',hdr, ' column')
			return
		else:
			column = array([float(row[cols[hdr]]) for row in csvrows])
			struct[hdr] = column.reshape((-1,1))
	return struct
			
#def selectdir(conffile = '.parsejpk_lastdir', indir = ''):
#	from Tkinter import Tk	# ugly, but functional
#	from tkFileDialog import askdirectory
#	from os.path import isfile, dirname, abspath
#	if isfile(conffile) and not indir:
#		with open(conffile, 'r') as cf:
#			indir  = cf.readline()
#	Tk().withdraw()
#	folder = askdirectory(initialdir = indir)
#	with open(conffile, 'w') as cf:
#		cf.write(dirname(abspath(folder)))
#	return folder

def parsejpkdir(folder = '', mode = 'v'):
	from os import listdir
	from os.path import isfile, join, isdir, split
	from numpy import hstack
	if not folder: folder = selectdir()
	f_ls = sorted([join(folder, f) for f in listdir(folder) if isfile(join(folder, f)) and f.endswith('.txt')])
	z, d, fnames, sensitivity, springConstant = [], [], [], [], []
	for f in f_ls:
		struct = parsejpkfile(f)
		z.append(struct['smoothedCapacitiveSensorHeight'])
		d.append(struct['vDeflection'])
		fnames.append(split(f))
		sensitivity.append(struct['sensitivity:']);
		springConstant.append(struct['springConstant:']);
	struct = {'z': hstack(z), 'd': hstack(d), 'file_names': fnames, 'sensitivity': sensitivity, 'springConstant':springConstant}
	return struct
	
def jpkmat(folder = '', arg = 'n'):
	from os import listdir, getcwd
	from os.path import isdir, join, abspath, pardir, basename
	from scipy.io import savemat
	from sys import stdout
	#if not folder: folder = selectdir()
	if not folder: folder = getcwd()
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
		dstruct = parsejpkdir(d, mode = 'v')
		if dstruct:
			savemat(join(abspath(join(d, pardir)), '.'.join([d,'mat'])), dstruct)
			with open(join(folder, 'springConstantIndex.csv'), 'a') as kInd: kInd.write(basename(d) + ', ' + str(dstruct['springConstant'][0]) + '\n') 
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
