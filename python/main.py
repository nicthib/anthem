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
	p_path = os.path.dirname(os.path.realpath(__file__))
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

def makekeys(cfg):
	keys = np.asarray(list(range(12)))
	notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	if cfg['scaletype'] == 'scale':
		keys = np.asarray([0, 2, 4, 5, 7, 9, 11])
	elif cfg['scaletype'] == 'chord':
		keys = np.asarray([0, 4, 7])
	if cfg['minor'] and cfg['scaletype'] == 'scale':
		keys[2] = 3
	elif cfg['minor'] and cfg['scaletype'] == 'chord':
		keys[1] = 3
	if cfg['scaletype'] == 'chord' and cfg['augment']:
		tmp = np.asarray([0, 2, 4, 5, 7, 9, 11])
		keys = np.append(keys,tmp[cfg['augment']-1])
	return keys + int(notes.index(cfg['key']))

def htoMIDI(cfg):
	dset = loadmat(os.path.join(p_path,cfg['pathin'], cfg['filein']))
	H = dset['H']
	fr = cfg['framerate']
	threshold = cfg['threshold']
	H = H[:, int(len(H[0]) * cfg['start']):int(len(H[0]) * cfg['stop'])]
	# Resample signals to msec
	ns = int(1000*len(H[0])/fr)
	H = signal.resample(H, ns, axis=1)
	# Force first and last samples to 0 to avoid edge cases
	H[:,0] = 0
	H[:,-1] = 0
	# Make MIDI key pattern
	keys = makekeys(cfg)
	keysfull = keys
	i = 1
	while len(keysfull) < len(H):
		keysfull = np.hstack((keysfull,keys+(12*i)))
		i += 1
	Hb = H > threshold
	Hb = Hb * 1
	Hmax = np.max(H)
	opts = {}
	opts['st'] = []
	opts['en'] = []
	opts['note'] = []
	opts['mag'] = []
	nd = [0, 0, 0, 0]
	MIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
	MIDI.addTempo(0,0,60)
	for i in range(len(H)):
		TC = np.diff(Hb[i, :])
		st = np.argwhere(TC == 1)
		en = np.argwhere(TC == -1)
		note = np.zeros((len(st), 1))
		mag = np.zeros((len(st), 1))
		for j in range(len(st)):
			tmp = H[i, np.asscalar(st[j]):np.asscalar(en[j])]
			mag[j] = int(np.max(tmp) * 7 / Hmax)
			note[j] = keysfull[i] + cfg['octave']*12
			MIDI.addNote(0, 0, int(note[j])+cfg['octave']*12, st[j]/1000, (en[j]-st[j])/1000, int( int(np.max(tmp) * 128 / Hmax)))
		opts['st'].extend(st)
		opts['en'].extend(en)
		opts['mag'].extend(mag[:])
		opts['note'].extend(note[:])
	opts['st'] = [x / 1000 for x in opts['st']]
	opts['en'] = [x / 1000 for x in opts['en']]
	file_name = os.path.join(p_path,cfg['pathout'],cfg['fileout']+'.mid')
	with open(file_name, 'wb') as output_file:
		MIDI.writeFile(output_file)

def htoaudio(cfg):
	dset = loadmat(os.path.join(p_path,cfg['pathin'], cfg['filein']))
	H = dset['H']
	fr = cfg['framerate']
	threshold = cfg['threshold']
	H = H[:, int(len(H[0]) * cfg['start']):int(len(H[0]) * cfg['stop'])]
	# Resample signals to msec
	ns = int(1000*len(H[0])/fr)
	H = signal.resample(H, ns, axis=1)
	# Force first and last samples to 0 to avoid edge cases
	H[:,0] = 0
	H[:,-1] = 0
	# Make MIDI key pattern
	keys = makekeys(cfg)
	keysfull = keys
	i = 1
	while len(keysfull) < len(H):
		keysfull = np.hstack((keysfull,keys+(12*i)))
		i += 1
	Hb = H > threshold
	Hb = Hb * 1
	Hmax = np.max(H)
	opts = {}
	opts['st'] = []
	opts['en'] = []
	opts['note'] = []
	opts['mag'] = []
	nd = [0, 0, 0, 0]
	MIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
	MIDI.addTempo(0,0,60)
	for i in range(len(H)):
		TC = np.diff(Hb[i, :])
		st = np.argwhere(TC == 1)
		en = np.argwhere(TC == -1)
		note = np.zeros((len(st), 1))
		mag = np.zeros((len(st), 1))
		for j in range(len(st)):
			tmp = H[i, np.asscalar(st[j]):np.asscalar(en[j])]
			mag[j] = int(np.max(tmp) * 7 / Hmax)
			note[j] = keysfull[i]
			MIDI.addNote(0, 0, int(note[j])+cfg['octave']*12, st[j]/1000, (en[j]-st[j])/1000, int( int(np.max(tmp) * 128 / Hmax)))
		opts['st'].extend(st)
		opts['en'].extend(en)
		opts['mag'].extend(mag[:])
		opts['note'].extend(note[:])
	opts['st'] = [x / 1000 for x in opts['st']]
	opts['en'] = [x / 1000 for x in opts['en']]
	opts['octave'] = [cfg['octave']] * len(opts['st'])
	wav = synth(ae,opts)
	file_name = os.path.join(p_path,cfg['pathout'],cfg['fileout'] + '.wav')
	write(file_name, 44100, wav)
	return opts, wav

def synth(ae,opts):
	raws = []
	fs = 44100
	r = .5 # release for note
	r_mat = np.linspace(1, 0, num=round(fs*r))
	for i in tqdm(range(0,len(opts['note']))):
		idx = int(opts['note'][i] + (opts['octave'][i] + 2)*12 + opts['mag'][i]*128)
		clip = range(fs*10*idx,fs*10*(idx+1))
		L = opts['en'][i][0] - opts['st'][i][0]		
		if L > 9.5-r:
			L = 9.5 - r	
		if L > 1:
			raw = ae['L'][0][clip]
		elif 1 > L > .25:
			raw = ae['M'][0][clip]
		elif L < .25:
			raw = ae['S'][0][clip]
		raw = raw[:int((L+r)*fs)] # Truncate to note length plus release
		raw[-round(fs*r):] *= np.vstack((r_mat,r_mat)).T
		if opts['st'][i][0] > 0:
			raw = np.vstack((np.zeros((int(fs*opts['st'][i][0]),2)),raw))
		raws.append(raw)
	maxraw = max(len(x) for x in raws)
	track = np.zeros((maxraw,2))
	for raw in raws:
		track[:len(raw)] = track[:len(raw)] + raw
	return track


	
