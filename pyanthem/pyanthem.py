import os, random, sys, cv2, time, csv, h5py
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from tkinter import *
from tkinter.ttk import Progressbar, Separator
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
from matplotlib.cm import *
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
		print('Audio engine downloaded to {}'.format(AE_path))
	else:
		print('Audio engine is already present in {}. If you want to uninstall, you must manually delete the AE folder.'.format(AE_path))

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
		print('No k given. Defaulting to {}...',end='').format(str(k))
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
	print('Decomposed data file saved to {}'.format(fn))

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

class GUI(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.package_path = os.path.split(os.path.realpath(__file__))[0]
		if __name__ == "__main__":
			self.AE_path = r'C:\Users\dnt21\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\pyanthem\AE'
		else:
			self.AE_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'AE')
		if os.path.isdir(self.AE_path):
			self.AE_run = True
		else:
			self.AE_run = False
		self.initGUI()
	
	def donothing(self):
		pass
	
	def loadfrommat(self):
		inputfile = os.path.normpath(fd.askopenfilename(title='Select .mat file for import',filetypes=[('.mat files','*.mat')]))
		if not inputfile:
			return None, None, None
		try:
			dh = loadmat(inputfile)
			self.H, self.W = dh['H'], dh['W']
			self.fr.set(float((dh['fr'])))
		except:
			self.status['text'] = 'Status: File load ERROR - please input a .mat file with variables H, W, and fr.'
			return
		self.W_shape = self.W.shape
		self.W = self.W.reshape(self.W.shape[0]*self.W.shape[1],self.W.shape[2])
		self.file_in.set(os.path.splitext(os.path.split(inputfile)[1])[0])
		self.file_out.set(self.file_in.get()+'_proc')
		self.save_path.set(os.path.split(inputfile)[0])

		# Set param defaults
		self.brightness.set(f'{float(f"{np.max(self.H):.3g}"):g}')
		self.threshold.set(f'{float(f"{np.mean(self.H):.3g}"):g}')
		self.Wshow_arr = list(range(len(self.H)))
		self.refreshplots()

	def refreshplots(self):
		if self.Wshow.get() == 'all':
			self.Wshow_arr = list(range(len(self.H)))
		elif re.match('^\[[0-9,: ]*\]$',self.Wshow.get()) is not None:
			w = eval('np.r_'+self.Wshow.get())
			self.Wshow_arr = np.asarray(list(range(len(self.H))))[w]
		else:
			self.status['text'] = 'Status: For \'components to show\', please input indices with commas and colons enclosed by square brackets, or \'all\' for all components.'
		self.H_pp = self.H[self.Wshow_arr,int(len(self.H.T)*self.st_p.get()/100):int(len(self.H.T)*self.en_p.get()/100)]
		self.H_pp = self.H_pp+self.baseline.get()
		self.W_pp = self.W[:,self.Wshow_arr]
		self.make_keys()
		self.H_to_Hp()
		self.init_plots()
		
		# Colormap
		cmaptmp = eval(self.cmapchoice.get())
		self.cmap = cmaptmp(np.linspace(0,1,len(self.H_pp)))

		# Update slider (Need to move the command)
		if self.frameslider.get() > len(self.H_pp.T): # This (usually) occurs when the user crops the dataset
			self.frameslider.set(1)
		self.frameslider['to'] = int(len(self.H_pp.T)-1)
		

		Hstd = self.H_pp.std()*3 # 3 Could be in an option json/yaml file
		if self.offsetH.get():
			tmpH = self.H_pp.T - repmat([w*Hstd for w in list(range(len(self.Wshow_arr)))],len(self.H_pp.T),1)
		else:
			tmpH = self.H_pp.T

		self.H_plot = self.Hax1.plot(tmpH,linewidth=.5)
		for i,j in enumerate(self.Hax1.lines):
			j.set_color(self.cmap[i])
		if not self.offsetH.get():
			thresh_line = self.Hax1.plot(np.ones((len(self.H_pp.T,)))*self.threshold.get(),linestyle='dashed',color='0',linewidth=1)
			baseline_line = self.Hax1.plot(np.ones((len(self.H_pp.T,)))*self.baseline.get(),linestyle='dashed',color='.5',linewidth=1)
			self.legend = self.Hax1.legend((thresh_line[0],baseline_line[0]), ('Threshold','Baseline'))

		if self.audio_format.get() == 'Stream':
			self.H_p_plot = self.Hax2.imshow(self.H_pp,interpolation='none',cmap=plt.get_cmap('gray'))
			self.H_p_plot.set_clim(0, np.max(self.H_pp))
		else:
			self.H_p_plot = self.Hax2.imshow(self.H_fp,interpolation='none',cmap=plt.get_cmap('gray'))

		self.Hax2.xaxis.set_major_formatter(tkr.FuncFormatter(lambda x, pos: '{:.2g}'.format(x/self.fr.get())))
		self.Hax2.set(xlabel='time (sec)',ylabel='Component #')

		self.Hax1.set_xlim(0, len(self.H_pp.T))
		self.Hax1.set_ylim(np.min(tmpH), np.max(tmpH))
		if self.offsetH.get():
			self.Hax1.set(ylabel='Component #')
		else:
			self.Hax1.set(ylabel='Magnitude')

		self.Hax1.spines['right'].set_visible(False)
		self.Hax1.spines['top'].set_visible(False)
		self.Hax1.spines['bottom'].set_visible(False)
		self.Hax1.tick_params(axis='x',which='both',bottom=False, top=False, labelbottom=False, right=False)

		if len(self.Wshow_arr) > 10:
			yticks = np.arange(4,len(self.H_pp),5)
			yticklabels = np.arange(5,len(self.H_pp)+1,5)
		else:
			yticks = np.arange(0,len(self.H_pp),1)
			yticklabels = np.arange(1,len(self.H_pp)+1,1)

		if self.offsetH.get():
			self.Hax1.set(yticks=-yticks*Hstd,yticklabels=yticklabels)
		self.Hax2.set(yticks=yticks,yticklabels=yticklabels)

		self.sc = 255/self.brightness.get()
		self.imWH = self.Wax1.imshow((self.W_pp@np.diag(self.H_pp[:,self.frameslider.get()])@self.cmap[:,:-1]*self.sc).reshape(self.W_shape[0],self.W_shape[1],3).clip(min=0,max=255).astype('uint8'))
		self.imW = self.Wax2.imshow((self.W_pp@self.cmap[:,:-1]*255/np.max(self.W_pp)).reshape(self.W_shape[0],self.W_shape[1],3).clip(min=0,max=255).astype('uint8'))
		
		self.H_p_plot.axes.set_aspect('auto')
		self.imW.axes.set_aspect('equal')
		self.imWH.axes.set_aspect('equal')
		self.canvas_H.draw()
		self.canvas_W.draw()
		self.refreshW_slider([])

	def refreshW_slider(self,event):
		if hasattr(self,'imWH'):
			self.imWH.remove()
		self.imWH = self.Wax1.imshow((self.W_pp@np.diag(self.H_pp[:,self.frameslider.get()])@self.cmap[:,:-1]*self.sc).reshape(self.W_shape[0],self.W_shape[1],3).clip(min=0,max=255).astype('uint8'))
		if hasattr(self,'H_vline'):
			self.H_vline.remove()
		self.H_vline, = self.Hax1.plot([],'k',linewidth=.5)
		self.H_vline.set_xdata([self.frameslider.get(), self.frameslider.get()])
		self.H_vline.set_ydata(self.Hax1.get_ylim())
		self.canvas_W.draw()
		self.canvas_H.draw()

	def H_to_Hp(self):
		ns = int(1000*len(self.H_pp.T)/self.fr.get())
		H = resample(self.H_pp, ns, axis=1)
		Hb = H > self.threshold.get()
		Hb = Hb * 1
		Hb[:,0] = 0
		Hb[:,-1] = 0
		Hmax = np.max(H)
		self.H_fp = np.zeros(np.shape(self.H_pp))
		self.nd = {}
		self.nd['st'],self.nd['en'],self.nd['note'],self.nd['mag'] = [],[],[],[]
		for i in range(len(H)):
			TC = np.diff(Hb[i,:])
			st = np.argwhere(TC == 1)
			en = np.argwhere(TC == -1)
			self.nd['st'].extend([x/1000 for x in st])
			self.nd['en'].extend([x/1000 for x in en])
			for j in range(len(st)):
				tmpmag = np.max(H[i,st[j][0]:en[j][0]])
				self.H_fp[i,int(st[j][0]*self.fr.get()/1000):int(en[j][0]*self.fr.get()/1000)] = tmpmag
				self.nd['mag'].append(int(tmpmag * 127 / Hmax))
				self.nd['note'].append(self.keys[i])

	def make_keys(self,value=[]):
		scaledata = []
		nnotes = len(self.H_pp)
		with open(os.path.join(self.package_path,'scaledata.csv')) as csvfile:
			file = csv.reader(csvfile)
			for row in file:
				scaledata.append([int(x) for x in row if x != 'NaN'])
		noteIDX = scaledata[self.scale_type_opts.index(self.scale_type.get())]
		noteIDX = [k+self.key_opts.index(self.key.get()) for k in noteIDX]
		keys = []
		for i in range(int(np.ceil(nnotes/len(noteIDX)))):
			keys.extend([k+i*12 for k in noteIDX])
		keys = keys[:nnotes] # Crop to nnotes to avoid confusion
		self.keys = [k+int(self.oct_add.get())*12 for k in keys]

	def htoaudio(self):
		# Make MIDI key pattern
		if self.audio_format.get() == 'MIDI':
			fn = os.path.join(self.save_path.get(),self.file_out.get())+'.mid'
			print(fn)
			MIDI = MIDIFile(1)  # One track
			MIDI.addTempo(0,0,60) # addTempo(track, time, tempo)
			for j in range(len(self.nd['note'])):
				# addNote(track, channel, pitch, time + i, duration, volume)
				MIDI.addNote(0, 0, self.nd['note'][j], self.nd['st'][j], (self.nd['en'][j]-self.nd['st'][j]), self.nd['mag'][j])
			with open(fn, 'wb') as mid:
				MIDI.writeFile(mid)
		elif self.audio_format.get() == 'Piano':
			self.synth()
		elif self.audio_format.get() == 'Stream':
			self.neuralstream()
	
	def preview_notes(self):
		if not self.AE_run:
			self.status['text'] = 'Status: AE engine not downloaded. Please do so using the function AE_download() to preview piano notes.'
		if get_init() is None: # Checks if pygame has initialized audio engine. Only needs to be run once per instance
			pre_init(44100, -16, 2, 1024)
			init()
			set_num_channels(128) # We will never need more than 128...
		for i in range(len(self.keys)):
			# Load/play notes
			if self.audio_format.get()!='Piano':
				sound = sine_wave(16.352*2**(self.keys[i]/12), 13000)
			else:
				fn = os.path.join(self.AE_path,str(self.keys[i])+'_5_2.ogg');
				sound = Sound(file=fn)
			self.imW.remove()
			Wtmp = self.W_pp[:,i]
			cmaptmp = self.cmap[i,:-1]
			self.imW = self.Wax2.imshow((Wtmp[:,None]@cmaptmp[None,:]*255/np.max(self.W_pp)).reshape(self.W_shape[0],self.W_shape[1],3).clip(min=0,max=255).astype('uint8'))
			self.canvas_W.draw()
			self.update()
			if self.audio_format.get()=='Stream':
				play_for(sound, 500)
			else:
				sound.play()
				time.sleep(.5)
		self.refreshplots()

	def synth(self):
		print('Keys are ' + str(self.nd['note']))
		fs = 44100
		r = .5 # release for note
		#r_mat = np.linspace(1, 0, num=int(fs*r))
		#r_mat = np.vstack((r_mat,r_mat)).T
		currnote = -1
		ext = 11
		note = [[0] * 8 for i in range(3)]
		raws = np.zeros((int(fs*(np.max(self.nd['st'])+ext)),2))
		for i in range(len(self.nd['st'])):
			if currnote != self.nd['note'][i]:
				currnote = self.nd['note'][i]
				for mag in range(8): # Load up new notes
					for length in range(3):
						fn = str(currnote+1)+'_'+str(mag)+'_'+str(length+1)+'.ogg';
						note[length][mag],notused = read(os.path.join(self.package_path,'AE',fn))
			L = self.nd['en'][i]-self.nd['st'][i]
			L = min(L,10-r)
			if L > 1:
				raw = note[2][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			elif 1 > L > .25:
				raw = note[1][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			elif L < .25:
				raw = note[0][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			#raw[-int(fs*r):] *= r_mat
			inds = range(int(self.nd['st'][i][0]*fs),int(self.nd['st'][i][0]*fs)+len(raw))
			raws[inds,:] += raw
			self.status['text'] = 'Status: writing audio file, {} out of {} notes written'.format(i+1,len(self.nd['st']))
			self.update()
		raws = raws[:-fs*(ext-1),:] # Crop wav
		raws = np.int16(raws/np.max(np.abs(raws)) * 32767)
		wavwrite(os.path.join(self.save_path.get(),self.file_out.get())+'.wav',fs,raws)
		self.status['text'] = 'Status: audio file written to {}'.format(self.save_path.get())

	def neuralstream(self):
		self.status['text'] = 'Writing audio file...'
		C0 = 16.352
		fs = 44100
		freqs = [C0*2**(i/12) for i in range(128)]
		ns = int(fs*len(self.H_fp.T)/self.fr.get())
		t1 = np.linspace(0,len(self.H_fp.T)/self.fr.get(),len(self.H_fp.T))
		t2 = np.linspace(0,len(self.H_fp.T)/self.fr.get(),ns)
		H = np.zeros((len(t2),))
		for n in range(len(self.H_fp)):
			Htmp = self.H_fp[n,:]
			Htmp[Htmp<0] = 0
			Htmp = interp1d(t1,Htmp)(t2)
			H += np.sin(2*np.pi*freqs[self.keys[n]]*t2)*Htmp
			self.status['text'] = 'Status: Writing audio: {} out of {} channels...'.format(n+1,len(self.H_fp))
			self.update()
		wav = np.hstack((H[:,None],H[:,None]))
		wav = np.int16(wav/np.max(np.abs(wav)) * 32767)
		wavwrite(os.path.join(self.save_path.get(),self.file_out.get())+'.wav',fs,wav)
		self.status['text'] = 'Status: audio file written to {}'.format(self.save_path.get())

	def exportavi(self):
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		out = cv2.VideoWriter(os.path.join(self.save_path.get(),self.file_out.get())+'.avi', fourcc, 20.0, tuple(self.W_shape[:-1]))
		for i in range(len(self.H_fp.T)):
			frame = (self.W_pp@np.diag(self.H_pp[:,i])@self.cmap[:,:-1]*self.sc).reshape(self.W_shape[0],self.W_shape[1],3).clip(min=0,max=255).astype('uint8')
			out.write(frame)
			self.status['text'] = 'Status: writing video file, {} out of {} frames written'.format(i,len(self.H_fp.T))
			self.update()
		out.release()
		self.status['text'] = 'Status: video file written to {}'.format(self.save_path.get())
	
	def combineAV(self):
		import moviepy.editor as mpe # Weird error when putting this in the main imports, so it goes here.
		fn = os.path.join(self.savepath.get(),self.fileout.get())
		my_clip = mpe.VideoFileClip(fn+'.avi')
		audio_background = mpe.AudioFileClip(fn+'.wav')
		final_clip = my_clip.set_audio(audio_background)
		final_clip.write_videofile(fn+'_AV.avi',fps=self.fr.get(),codec='mpeg4')
		os.remove(fn+'.avi')
		os.remove(fn+'.wav')
		self.status['text'] = 'Status: video file w/ audio written to {}'.format(self.savepath.get())

	def editsave_path(self):
		self.save_path.set(fd.askdirectory(title='Select a directory to save output files',initialdir=self.save_path.get()))

	def initGUI(self):
		# StringVars		
		self.file_in=init_entry('...')
		self.file_out=init_entry('...')
		self.save_path=init_entry('...')
		self.fr=init_entry(10)
		self.st_p=init_entry(0)
		self.en_p=init_entry(100)
		self.baseline=init_entry(0)
		self.filterH=init_entry(0)
		self.brightness=init_entry(0)
		self.threshold=init_entry(0)
		self.oct_add = init_entry('2')
		self.scale_type = init_entry('Chromatic (12/oct)')
		self.key = init_entry('C')
		self.audio_format = init_entry('Stream')
		self.Wshow=init_entry('all')
		self.status = init_entry('Status: Welcome to pyanthem!')
		self.cmapchoice = init_entry('jet')
		# Labels

		Label(text='').grid(row=0,column=0)
		Label(text='File Parameters',font='Helvetica 14 bold').grid(row=0,column=1,columnspan=2,sticky='WE')
		Label(text='Movie Parameters',font='Helvetica 14 bold').grid(row=0,column=3,columnspan=2,sticky='WE')
		Label(text='Audio Parameters',font='Helvetica 14 bold').grid(row=0,column=5,columnspan=2,sticky='WE')
		Label(text='Input Filename').grid(row=1, column=1,columnspan=2,sticky='W')
		Label(textvariable=self.file_in).grid(row=2, column=1,columnspan=2,sticky='W')
		Label(text='Output Filename').grid(row=3, column=1,columnspan=2,sticky='W')
		Label(text='Output Save Path').grid(row=5, column=1,columnspan=2,sticky='W')
		Message(textvariable=self.save_path,aspect=500).grid(row=6, column=1,columnspan=2,sticky='W')
		Label(text='Framerate').grid(row=1, column=3, sticky='E')
		Label(text='Start (%)').grid(row=2, column=3, sticky='E')
		Label(text='End (%)').grid(row=3, column=3, sticky='E')
		Label(text='Baseline').grid(row=4, column=3, sticky='E')
		Label(text='HP filter').grid(row=5, column=3, sticky='E')
		Label(text='Max brightness').grid(row=6, column=3, sticky='E')
		Label(text='Colormap').grid(row=7, column=3, sticky='E')
		Label(text='Threshold').grid(row=1, column=5, sticky='E')
		Label(text='Octave').grid(row=2, column=5, sticky='E')
		Label(text='Scale Type').grid(row=3, column=5, sticky='E')
		Label(text='Key').grid(row=4, column=5, sticky='E')
		Label(text='Audio format').grid(row=5, column=5, sticky='E')
		self.status = Message(text='Status: welcome to pyathem!',aspect=1000)
		self.status.grid(row=8, column=1,columnspan=4)

		# Entries
		Entry(textvariable=self.file_out).grid(row=4, column=1,columnspan=2,sticky='W')
		Entry(textvariable=self.fr,width=7).grid(row=1, column=4, sticky='W')
		Entry(textvariable=self.st_p,width=7).grid(row=2, column=4, sticky='W')
		Entry(textvariable=self.en_p,width=7).grid(row=3, column=4, sticky='W')
		Entry(textvariable=self.baseline,width=7).grid(row=4, column=4, sticky='W')
		Entry(textvariable=self.filterH,width=7).grid(row=5, column=4, sticky='W')
		Entry(textvariable=self.brightness,width=7).grid(row=6, column=4, sticky='W')
		Entry(textvariable=self.threshold,width=7).grid(row=1, column=6, sticky='W')
		#self.Wshow = Entry(text='',width=5).grid(row=109, column=4, columnspan=3)

		# Buttons
		Button(text='Edit save path',width=15,command=self.editsave_path).grid(row=7, column=1,columnspan=2)
		Button(text='Preview Notes',width=15,command=self.preview_notes).grid(row=6, column=5,columnspan=2)
		Button(text='Update',width=15,command=self.refreshplots).grid(row=8, column=5,columnspan=2)

		# Options
		self.oct_add_opts = ['0','1','2','3','4','5']
		self.scale_type_opts = ['Chromatic (12/oct)','Major scale (7/oct)','Minor scale (7/oct)', 
		'Maj. triad (3/oct)','Min. triad (3/oct)','Aug. triad (3/oct)',
		'Dim. triad (3/oct)','Maj. 6th (4/oct)','Min. 6th (4/oct)',
		'Maj. 7th (4/oct)','Min. 7th (4/oct)','Aug. 7th (4/oct)',
		'Dim. 7th (4/oct)','Maj. 7/9 (5/oct)','Min. 7/9 (5/oct)']
		self.key_opts = ['C','C#/D♭','D','D#/E♭','E','F','F#/G♭','G','G#/A♭','A','A#/B♭','B']
		self.cmaps = sorted(['viridis', 'plasma', 'inferno', 'magma', 'cividis','binary', 
		'bone', 'pink','spring', 'summer', 'autumn', 'winter', 'cool','hot','copper','Spectral', 
		'coolwarm', 'bwr', 'seismic','twilight', 'hsv', 'Paired', 'Accent','Dark2', 'prism', 'ocean', 
		'terrain', 'CMRmap','brg', 'rainbow', 'jet'],key=lambda s: s.lower())
		if self.AE_run:
			self.audio_format_opts = ['Stream','Piano','MIDI']
		else:
			self.audio_format_opts = ['Stream','MIDI']
			self.status['text'] = 'Status: AE engine not downloaded. Please do using AE_download() to enable "Piano" format'

		# Option Menus
		OptionMenu(self,self.oct_add,*self.oct_add_opts,command=self.make_keys).grid(row=2, column=6, sticky='W')
		OptionMenu(self,self.scale_type,*self.scale_type_opts,command=self.make_keys).grid(row=3, column=6, sticky='W')
		OptionMenu(self,self.key,*self.key_opts,command=self.make_keys).grid(row=4, column=6, sticky='W')
		OptionMenu(self,self.audio_format,*self.audio_format_opts,command=self.make_keys).grid(row=5, column=6, sticky='W')
		OptionMenu(self,self.cmapchoice,*self.cmaps).grid(row=7, column=4, sticky='WE')

		# Menu bar
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Load from .mat", command=self.loadfrommat)
		filemenu.add_command(label="Load from config", command=self.donothing)
		filemenu.add_command(label="Quit",command=lambda:[self.quit(),self.destroy(),quit()])

		savemenu = Menu(menubar, tearoff=0)
		savemenu.add_command(label="Audio", command=self.htoaudio)
		savemenu.add_command(label="Video", command=self.exportavi)
		savemenu.add_command(label="Combine A/V", command=self.combineAV)
		savemenu.add_command(label="Config File", command=self.donothing)

		menubar.add_cascade(label="File", menu=filemenu)
		menubar.add_cascade(label="Save", menu=savemenu)
		self.config(menu=menubar)

		# Seperators
		Separator(self, orient='vertical').grid(column=0, row=0, rowspan=9, sticky='nse')
		Separator(self, orient='vertical').grid(column=2, row=0, rowspan=8, sticky='nse')
		Separator(self, orient='vertical').grid(column=4, row=0, rowspan=8, sticky='nse')
		Separator(self, orient='vertical').grid(column=6, row=0, rowspan=9, sticky='nse')
		Separator(self, orient='horizontal').grid(column=1, row=0, columnspan=6,sticky='nwe')
		Separator(self, orient='horizontal').grid(column=1, row=0, columnspan=6,sticky='swe')
		Separator(self, orient='horizontal').grid(column=1, row=7, columnspan=6,sticky='swe')
		Separator(self, orient='horizontal').grid(column=1, row=8, columnspan=6,sticky='swe')
		Separator(self, orient='horizontal').grid(column=1, row=2, columnspan=2,sticky='swe')
		Separator(self, orient='horizontal').grid(column=1, row=4, columnspan=2,sticky='swe')
		Separator(self, orient='horizontal').grid(column=1, row=6, columnspan=2,sticky='swe')

		# Offset var
		self.offsetH = IntVar()
		self.offsetH.set(1)
		
		# frameslider var 
		self.frameslider = Scale(self, from_=0, to=1, orient=HORIZONTAL)
		self.frameslider['command'] = self.refreshW_slider

	def init_plots(self):
		# H
		self.figH = plt.Figure(figsize=(7,6), dpi=100, tight_layout=True)
		self.Hax1 = self.figH.add_subplot(211)
		self.Hax2 = self.figH.add_subplot(212)
		self.Hax1.set_title('Raw Temporal Data (H)')
		self.Hax2.set_title('Converted Temporal Data (H\')')
		self.canvas_H = FigureCanvasTkAgg(self.figH, master=self)
		self.canvas_H.draw()
		self.canvas_H.get_tk_widget().grid(row=0,column=7,rowspan=29,columnspan=10)

		# Checkbox
		Checkbutton(self, text="Offset H",bg='white',command=self.refreshplots,variable=self.offsetH).grid(row=7,rowspan=4,column=16)

		# W
		self.figW = plt.Figure(figsize=(6,3), dpi=100, constrained_layout=True)
		self.Wax1 = self.figW.add_subplot(121)
		self.Wax2 = self.figW.add_subplot(122)

		self.Wax1.set_title('Output(H x W)')
		self.Wax2.set_title('Spatial Components (W)')
		self.Wax1.axis('off')
		self.Wax2.axis('off')
		self.canvas_W = FigureCanvasTkAgg(self.figW, master=self)
		self.canvas_W.draw()
		self.canvas_W.get_tk_widget().grid(row=9,column=1,rowspan=20,columnspan=6)
		
		# Frameslider
		self.frameslider.grid(row=29, column=1, columnspan=3, sticky='EW')

		# Wshow
		Label(text='Components to show:').grid(row=29, column=3, columnspan=3, sticky='E')
		Entry(textvariable=self.Wshow,width=20,justify='center').grid(row=29, column=5, columnspan=2,sticky='E')
		

if __name__ == "__main__":
	MainWindow = GUI()
	MainWindow.mainloop()