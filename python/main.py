from pathlib import Path
from scipy.io import loadmat, whosmat
from scipy.io.wavfile import write
from scipy import signal
import numpy as np
from tqdm import tqdm
from soundfile import read
from midiutil import MIDIFile
import os, random, sys
import importlib
from tkinter import *
import  tkinter.ttk as ttk
from tkinter import filedialog as fd 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from functools import partial
from matplotlib import cm

def init_audio_engine():
	print('Intializing...')
	global p_path
	
	p_path = "/".join(p_path.split('/')[:-1]) # Go up one dir
	global ae
	ae = {}
	ae_t = ['S','M','L']
	for i in range(3):
		ae[ae_t[i]] = read(os.path.join(p_path,'audio', 'ae_' +  ae_t[i] + '.ogg'))
	print('Done!')

def init_cfg():
	cfg = {}
	cfg['scaletype'] = 'scale'
	cfg['minor'] = 0
	cfg['augment'] = 0
	cfg['key'] = 'C'
	cfg['framerate'] = 10
	cfg['start'] = 0
	cfg['stop'] = .1
	cfg['threshold'] = .01
	cfg['octave'] = 1
	cfg['pathin'] = 'inputs'
	cfg['pathout'] = 'outputs'
	cfg['fileout'] = 'out'
	cfg['filein'] = 'demo1.mat'
	return cfg

def makekeys(key,scaletype,addoct,nnotes):
	# noteref = csvread('NoteIDX.csv') FIX
	noteIDX = noteref[scaletype,:]
	#noteIDX(isnan(noteIDX)) = [] # FIX
	keys = noteIDX+key;
	keysout = []
	for i in range(ceil(nnotes/numel(noteIDX))):
		keysout.append(keys+(i-1)*12)
	keysout = keysout[:nnotes];
	keysout = keysout+addoct*12;

def jet(dz):
	tmp = cm.jet(plt.Normalize(0,dz-1)(range(dz)))
	return tmp[:,:-1]

def donothing():
	pass

def init_entry(fn):
	if isinstance(fn, str):
		entry = StringVar()
	else:
		entry = DoubleVar()
	entry.set(fn)
	return entry

def H_to_Hp(H,fr,threshold):
	keysfull = range(20)
	ns = int(1000*len(H.T)/fr)
	H = signal.resample(H, ns, axis=1)
	Hb = H > threshold
	Hb = Hb * 1
	Hb[:,0] = 0
	Hb[:,-1] = 0
	Hmax = np.max(H)
	Hp = np.zeros(np.shape(H))
	nd = {}
	nd['st'],nd['en'],nd['note'],nd['mag'] = [],[],[],[]
	for i in range(len(H)):
		TC = np.diff(Hb[i,:])
		st = np.argwhere(TC == 1)
		en = np.argwhere(TC == -1)
		nd['st'].extend([x/1000 for x in st])
		nd['en'].extend([x/1000 for x in en])
		for j in range(len(st)):
			tmpmag = np.max(H[i,st[j][0]:en[j][0]])
			Hp[i,st[j][0]:en[j][0]] = tmpmag
			nd['mag'].append(int(tmpmag * 127 / Hmax))
			nd['note'].append(keysfull[i])
		# Add this data to the nd file
		
	return Hp,nd

#def htoMIDI(cfg):
# 	dset = loadmat(os.path.join(p_path,cfg['pathin'], cfg['filein']))
# 	H = dset['H']
# 	fr = cfg['framerate']
# 	threshold = cfg['threshold']
# 	H = H[:, int(len(H[0]) * cfg['start']):int(len(H[0]) * cfg['stop'])]
# 	# Resample signals to msec
# 	ns = int(1000*len(H[0])/fr)
# 	H = signal.resample(H, ns, axis=1)
# 	# Force first and last samples to 0 to avoid edge cases
# 	H[:,0] = 0
# 	H[:,-1] = 0
# 	# Make MIDI key pattern
# 	keys = makekeys(cfg)
# 	keysfull = keys
# 	i = 1
# 	while len(keysfull) < len(H):
# 		keysfull = np.hstack((keysfull,keys+(12*i)))
# 		i += 1
# 	Hb = H > threshold
# 	Hb = Hb * 1
# 	Hmax = np.max(H)
# 	opts = {}
# 	opts['st'] = []
# 	opts['en'] = []
# 	opts['note'] = []
# 	opts['mag'] = []
# 	nd = [0, 0, 0, 0]
# 	MIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
# 	MIDI.addTempo(0,0,60)
# 	for i in range(len(H)):
# 		TC = np.diff(Hb[i, :])
# 		st = np.argwhere(TC == 1)
# 		en = np.argwhere(TC == -1)
# 		note = np.zeros((len(st), 1))
# 		mag = np.zeros((len(st), 1))
# 		for j in range(len(st)):
# 			tmp = H[i, np.asscalar(st[j]):np.asscalar(en[j])]
# 			mag[j] = int(np.max(tmp) * 7 / Hmax)
# 			note[j] = keysfull[i] + cfg['octave']*12
# 			MIDI.addNote(0, 0, int(note[j])+cfg['octave']*12, st[j]/1000, (en[j]-st[j])/1000, i)))
# 		opts['st'].extend(st)
# 		opts['en'].extend(en)
# 		opts['mag'].extend(mag[:])
# 		opts['note'].extend(note[:])
# 	opts['st'] = [x / 1000 for x in opts['st']]
# 	opts['en'] = [x / 1000 for x in opts['en']]
# 	file_name = os.path.join(p_path,cfg['pathout'],cfg['fileout']+'.mid')
# 	with open(file_name, 'wb') as output_file:
# 		MIDI.writeFile(output_file)

