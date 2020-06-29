import os, random, sys, cv2, time, csv, pickle
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from tkinter import *
from tkinter.ttk import Progressbar, Separator, Combobox
from tkinter import filedialog as fd 
from scipy.io import loadmat, savemat, whosmat
from scipy.io.wavfile import write as wavwrite
from scipy.optimize import nnls
from scipy.interpolate import interp1d
from scipy.signal import resample
from pygame.mixer import Sound, init, quit, get_init, set_num_channels, pre_init
from pygame.sndarray import make_sound
from pygame.time import delay
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cmaps
#https://matplotlib.org/gallery/color/colormap_reference.html
import matplotlib.ticker as tkr
import numpy as np
from numpy.matlib import repmat
from soundfile import read
from midiutil import MIDIFile
from git import Repo
from sklearn.cluster import KMeans

def AE_download():
	AE_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'AE')
	if not os.path.isdir(AE_path):
		print('Cloning the audio engine to the pyanthem package directory...')
		Repo.clone_from('https://github.com/nicthib/AE.git',AE_path)
		print(f'Audio engine downloaded to {AE_path}')
	else:
		print(f'Audio engine is already present in {AE_path}. If you want to uninstall, you must manually delete the AE folder.')

def init_entry(fn):
	if isinstance(fn, str):
		entry = StringVar()
	else:
		entry = DoubleVar()
	entry.set(fn)
	return entry

def process_raw(k=[],fr=[]):
	root = Tk()
	root.withdraw()
	file = os.path.normpath(fd.askopenfilename(title='Select .mat file for import',filetypes=[('.mat files','*.mat')]))
	if len(file) == 0:
		return
	root.update()
	dh,var = loadmat(file),whosmat(file)
	data = dh[var[0][0]]
	sh = data.shape
	if len(sh) != 3:
		print('ERROR: input dataset is not 3D.')
		return
	data = data.reshape(sh[0]*sh[1],sh[2])
	# Ignore rows with any nans
	nanidx = np.any(np.isnan(data), axis=1)
	data_nn = data[~nanidx] # nn=non-nan
	# k-means
	print('Performing k-means...',end='')
	if k == []:
		k = int(len(data)**.25) # Default k is the 4th root of the number of samples per frame (for 256x256, this would be 16)
		print(f'No k given. Defaulting to {k}...',end='')
	idx_nn = KMeans(n_clusters=k, random_state=0).fit(data_nn).labels_
	idx = np.zeros((len(data),))
	idx[nanidx==False] = idx_nn
	# TCs
	H = np.zeros((k,len(data.T)))
	for i in range(k):
		H[i,:] = np.nanmean(data[idx==i,:],axis=0)
	print('done.')
	# NNLS
	nnidx=np.where(~nanidx)[0]
	W = np.zeros((len(data),k))
	print('Performing NNLS...',end='')
	for i in range(len(nnidx)):
		W[nnidx[i],:]=nnls(H.T,data_nn[i,:])[0]
	# Sort top to bottom
	xc,yc = [], []
	(X,Y) = np.meshgrid(range(sh[0]),range(sh[1]))
	for i in range(len(W.T)):
		Wtmp = W[:,i].reshape(sh[0],sh[1])
		xc.append((X*Wtmp).sum() / Wtmp.sum().astype("float"))
		yc.append((Y*Wtmp).sum() / Wtmp.sum().astype("float"))
	I = np.argsort(yc)
	W = W[:,I]
	H = H[I,:]
	print('done.')
	# Assign variables and save
	df = {}
	df['H'] = H
	df['W'] = W.reshape(sh[0],sh[1],k)
	if fr == []:
		df['fr'] = 10
		print('No fr given. Defaulting to 10')
	else:
		df['fr'] = fr
	fn = file.replace('.mat','_decomp.mat')
	savemat(fn,df)
	print(f'Decomposed data file saved to {fn}')

def play_for(sample_wave, ms):
	sound = make_sound(sample_wave)
	sound.play(-1)
	delay(ms)
	sound.stop()
	
def sine_wave(hz, peak, n_samples=22000):
	length = 44100 / float(hz)
	omega = np.pi * 2 / length
	xvalues = np.arange(int(length)) * omega
	onecycle = peak * np.sin(xvalues)
	sound = np.resize(onecycle, (n_samples,))
	env = np.ones(len(sound),)
	attack = int(44100*.15)
	env[:attack] = np.linspace(0,1,attack)
	env[-attack:] = np.linspace(1,0,attack)
	sound=sound*env
	sound = np.hstack((sound[:,None],sound[:,None]))
	return sound.astype(np.int16)