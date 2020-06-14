from main import *


class App_Window(Tk):
	def __init__(self,parent):
		Tk.__init__(self,parent)
		self.parent = parent
		self.init()

	def loadfrommat(self):
		vp = Toplevel(self)
		self.inputfile = fd.askopenfilename(title='Select .mat file for import',filetypes=[('.mat files','*.mat')])
		if not self.inputfile:
			vp.destroy()
			return None, None, None
		vp.attributes("-topmost", True)
		vs = whosmat(self.inputfile)
		vname,vsize = [v[0] for v in vs],[v[1] for v in vs]

		# Layout dropdowns and quit button
		Label(vp,text='Temporal variable').grid(row=0,column=0, padx=20)
		Label(vp,text='Spatial variable').grid(row=0,column=1, padx=20)
		varH = StringVar(vp)
		varH.set(vname[0])
		varW = StringVar(vp)
		varW.set(vname[0])
		OptionMenu(vp,varH,*vname).grid(row=1, column=0)
		OptionMenu(vp,varW,*vname).grid(row=1, column=1)
		Button(vp,text='Done',command=lambda:[vp.quit(),vp.destroy()],width=10).grid(row=2,column=0,columnspan=3)
		vp.mainloop()
		dh = loadmat(self.inputfile)
		self.H, self.W = dh[varH.get()], dh[varW.get()]
		self.ss = self.W.shape
		self.W = self.W.reshape(self.W.shape[0]*self.W.shape[1],self.W.shape[2])
		self.framenum = 1
		self.brightness.set(f'{float(f"{np.max(self.H):.3g}"):g}')
		self.filein.set(os.path.split(self.inputfile)[1])
		self.fileout.set(os.path.split(self.inputfile)[1])
		self.savepath.set(os.path.split(self.inputfile)[0].replace('input','output'))
		self.init_plots()
		self.refreshH()
		self.refreshW()

	def refreshH(self):
		# H_pp is pre-processed
		# H_fp is fully processed
		self.H_pp = self.H[:,int(len(self.H.T)*self.st_p.get()/100):int(len(self.H.T)*self.en_p.get()/100)] + self.baseline.get()
		if self.audio_fmt.get() != 'Stream':
			self.H_to_Hp()
		else:
			self.H_fp = self.H_pp

		self.init_plots()
		
		self.H_plot = self.Hax1.plot(self.H_pp.T,linewidth=.5)
		self.H_p_plot = self.Hax2.imshow(self.H_fp,interpolation='none')
		self.H_p_plot.axes.set_aspect('auto')

		ax = self.canvas_H.figure.axes[0]
		ax.set_xlim(0, len(self.H_pp.T))
		ax.set_ylim(np.min(self.H_pp), np.max(self.H_pp)) 
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		
		self.canvas_H.draw()

	def refreshW(self):
		self.cmap = jet(len(self.H))
		self.sc = 255/self.brightness.get()
		self.imWH = self.Wax1.imshow((self.W@np.diag(self.H_pp[:,self.framenum])@self.cmap*self.sc).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.imWH.axes.set_aspect('equal')
		self.imW = self.Wax2.imshow((self.W@self.cmap*255/np.max(self.W)).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.imW.axes.set_aspect('equal')
		self.canvas_W.draw()

		# Update slider max min
		self.frameslider['to'] = int(len(self.H_pp.T)-1)
		self.frameslider['command'] = self.refreshW_slider
		plt.tight_layout()

	def refreshW_slider(self,event):
		self.imWH.remove()
		self.imWH = self.Wax1.imshow((self.W@np.diag(self.H_pp[:,self.frameslider.get()])@self.cmap*self.sc).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.canvas_W.draw()

	def H_to_Hp(self):
		keysfull = range(20)
		ns = int(1000*len(self.H_pp.T)/self.fr.get())
		H = signal.resample(self.H_pp, ns, axis=1)
		Hb = H > self.thresh.get()
		Hb = Hb * 1
		Hb[:,0] = 0
		Hb[:,-1] = 0
		Hmax = np.max(H)
		self.H_fp = np.zeros(np.shape(H))
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
				self.H_fp[i,st[j][0]:en[j][0]] = tmpmag
				self.nd['mag'].append(int(tmpmag * 127 / Hmax))
				self.nd['note'].append(keysfull[i])

	def htoaudio(self):
		# Make MIDI key pattern
		self.keys = range(0,20)#self.makekeys() # addoct here
		if self.audio_fmt.get() == 'MIDI':
			MIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
			MIDI.addTempo(0,0,60)
			for i in range(len(nd)):
				MIDI.addNote(0, 0, int(self.nd['note'][j]), self.nd['st'][j]/1000, (self.nd['en'][j]-self.nd['st'][j])/1000, self.nd['mag'][j])
			with open(file_name, 'wb') as output_file:
				MIDI.writeFile(os.path.combine(self.savepath.get(),self.fileout.get()))
		elif self.audio_fmt.get() == 'Dynamic':
			wav = self.synth()
		elif self.audio_fmt.get() == 'Stream':
			pass
			# neural stream here!

	def synth(self):
		fs = 44100
		r = .5 # release for note
		r_mat = np.linspace(1, 0, num=int(fs*r))
		r_mat = np.vstack((r_mat,r_mat)).T
		p_path = self.savepath.get().replace('outputs','AE')
		currnote = -1
		ext = 11
		note = [[0] * 8 for i in range(3)]
		raws = np.zeros((int(fs*(np.max(self.nd['st'])+ext)),2))
		for i in tqdm(range(len(self.nd['st']))):
			if currnote != self.nd['note'][i]:
				currnote = self.nd['note'][i]
				for mag in range(8): # Load up new notes
					for length in range(3):
						fn = str(currnote+1)+'_'+str(mag)+'_'+str(length+1)+'.ogg';
						note[length][mag],notused = read(os.path.join(p_path,fn))
			L = self.nd['en'][i]-self.nd['st'][i]
			if L > 9.5-r:
				L = 9.5 - r
			if L > 1:
				raw = note[2][int(np.ceil(self.nd['mag'][i]/16-1))][0:int((L+r)*fs)] # Truncate to note length plus release
			elif 1 > L > .25:
				raw = note[1][int(np.ceil(self.nd['mag'][i]/16-1))][0:int((L+r)*fs)] # Truncate to note length plus release
			elif L < .25:
				raw = note[0][int(np.ceil(self.nd['mag'][i]/16-1))][0:int((L+r)*fs)] # Truncate to note length plus release
			raw[-int(fs*r):] *= r_mat
			inds = range(int(self.nd['st'][i][0]*fs),int(self.nd['st'][i][0]*fs)+len(raw))
			raws[inds,:] += raw
		raws = raws[:-fs*(ext-1),:] # Crop wav
		write(os.path.join(self.savepath.get(),os.path.splitext(self.fileout.get())[0]+'.wav'),fs,raws)

	def editsavepath(self):
		self.savepath.set(fd.askdirectory(title='Select a directory to save output files',initialdir=self.savepath.get()))

	def init(self):
		# StringVars
		self.filein=init_entry('...')
		self.fileout=init_entry('...')
		self.savepath=init_entry('...')
		self.fr=init_entry(10)
		self.st_p=init_entry(0)
		self.en_p=init_entry(100)
		self.baseline=init_entry(0)
		self.filterH=init_entry(0)
		self.brightness=init_entry(0)
		self.thresh=init_entry(0)
		
		self.oct_add = init_entry('0')
		self.scaletype = init_entry('Chromatic (12/oct)')
		self.key = init_entry('C')
		self.audio_fmt = init_entry('Stream')

		# Labels
		Label(text='').grid(row=0,column=0)
		Label(text='Input Filename').grid(row=1, column=1,columnspan=2,sticky='W')
		Label(textvariable=self.filein).grid(row=2, column=1,columnspan=2,sticky='W')
		Label(text='Output Filename').grid(row=3, column=1,columnspan=2,sticky='W')
		Label(text='Output Save Path').grid(row=5, column=1,columnspan=2,sticky='W')
		Label(textvariable=self.savepath, wraplength=500).grid(row=6, column=1,columnspan=2,sticky='W')
		Label(text='Framerate').grid(row=1, column=3, sticky='E')
		Label(text='Start (%)').grid(row=2, column=3, sticky='E')
		Label(text='End (%)').grid(row=3, column=3, sticky='E')
		Label(text='Baseline').grid(row=4, column=3, sticky='E')
		Label(text='HP filter').grid(row=5, column=3, sticky='E')
		Label(text='Max brightness').grid(row=6, column=3, sticky='E')
		Label(text='Threshold').grid(row=1, column=5, sticky='E')
		Label(text='Octave').grid(row=2, column=5, sticky='E')
		Label(text='Scale Type').grid(row=3, column=5, sticky='E')
		Label(text='Key').grid(row=4, column=5, sticky='E')
		Label(text='Audio format').grid(row=5, column=5, sticky='E')
		st = Label(text='Status:').grid(row=8, column=1,columnspan=4, sticky='W')
		#Label(text='Components to show').grid(row=108, column=5)

		# Entries
		Entry(textvariable=self.fileout).grid(row=4, column=1,columnspan=2,sticky='W')
		Entry(textvariable=self.fr,width=7).grid(row=1, column=4, sticky='W')
		Entry(textvariable=self.st_p,width=7).grid(row=2, column=4, sticky='W')
		Entry(textvariable=self.en_p,width=7).grid(row=3, column=4, sticky='W')
		Entry(textvariable=self.baseline,width=7).grid(row=4, column=4, sticky='W')
		Entry(textvariable=self.filterH,width=7).grid(row=5, column=4, sticky='W')
		Entry(textvariable=self.brightness,width=7).grid(row=6, column=4, sticky='W')
		Entry(textvariable=self.thresh,width=7).grid(row=1, column=6, sticky='W')
		#self.Wshow = Entry(text='',width=5).grid(row=109, column=4, columnspan=3)

		# Buttons
		Button(text='Edit save path',width=20,command=self.editsavepath).grid(row=7, column=1,columnspan=2)
		Button(text='Play Notes',width=20).grid(row=6, column=5,columnspan=2)
		Button(text='Update',command=lambda:[self.refreshH(),self.refreshW()]).grid(row=8, column=5,columnspan=2,sticky='WE')

		# Options
		self.oct_add_opts = ['0','1','2','3','4','5']
		self.scaletype_opts = ['Chromatic (12/oct)','Major scale (7/oct)','Minor scale (7/oct)', 
		'Maj. triad (3/oct)','Min. triad (3/oct)','Aug. triad (3/oct)',
		'Dim. triad (3/oct)','Maj. 6th (4/oct)','Min. 6th (4/oct)',
		'Maj. 7th (4/oct)','Min. 7th (4/oct)','Aug. 7th (4/oct)',
		'Dim. 7th (4/oct)','Maj. 7/9 (5/oct)','Min. 7/9 (5/oct)']
		self.key_opts = ['C','C#/D♭','D','D#/E♭','E','F','F#/G♭','G','G#/A♭','A','A#/B♭','B']
		self.audio_fmt_opts = ['Stream','Dynamic','MIDI']

		# Option Menus
		OptionMenu(self,self.oct_add,*self.oct_add_opts).grid(row=2, column=6, sticky='W')
		OptionMenu(self,self.scaletype,*self.scaletype_opts).grid(row=3, column=6, sticky='W')
		OptionMenu(self,self.key,*self.key_opts).grid(row=4, column=6, sticky='W')
		OptionMenu(self,self.audio_fmt,*self.audio_fmt_opts).grid(row=5, column=6, sticky='W')

		# Menu bar
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Load from .mat", command=self.loadfrommat)
		filemenu.add_command(label="Load from config", command=donothing)
		filemenu.add_command(label="Quit", command=self.quit)

		savemenu = Menu(menubar, tearoff=0)
		savemenu.add_command(label="Audio", command=self.htoaudio)
		savemenu.add_command(label="Video", command=donothing)
		savemenu.add_command(label="Combine A/V", command=donothing)
		savemenu.add_command(label="Config File", command=donothing)

		menubar.add_cascade(label="File", menu=filemenu)
		menubar.add_cascade(label="Save", menu=savemenu)
		self.config(menu=menubar)

		# Seperators
		ttk.Separator(self, orient='vertical').grid(column=0, row=1, rowspan=8, sticky='nse')
		ttk.Separator(self, orient='vertical').grid(column=2, row=1, rowspan=7, sticky='nse')
		ttk.Separator(self, orient='vertical').grid(column=4, row=1, rowspan=7, sticky='nse')
		ttk.Separator(self, orient='vertical').grid(column=6, row=1, rowspan=8, sticky='nse')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=0, columnspan=6,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=7, columnspan=6,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=8, columnspan=6,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=2, columnspan=2,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=4, columnspan=2,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=6, columnspan=2,sticky='swe')
		self.update()

	def init_plots(self):
		# Plot H
		self.figH = plt.Figure(figsize=(6,6), dpi=100)
		self.Hax1 = self.figH.add_subplot(211)
		self.Hax2 = self.figH.add_subplot(212)
		self.Hax1.set_title('Raw Temporal Data (H)')
		self.Hax2.set_title('Converted Temporal Data (H\')')
		self.Hax1.axis('off')
		self.Hax2.axis('off')
		self.canvas_H = FigureCanvasTkAgg(self.figH, master=self)
		self.canvas_H.draw()
		self.canvas_H.get_tk_widget().grid(row=0,column=7,rowspan=29,columnspan=1)

		# Plot W
		self.figW = plt.Figure(figsize=(6,3), dpi=100)
		self.Wax1 = self.figW.add_subplot(121)
		self.Wax2 = self.figW.add_subplot(122)
		self.Wax1.set_title('Output(H x W)')
		self.Wax2.set_title('Spatial Components (W)')
		self.Wax1.axis('off')
		self.Wax2.axis('off')
		self.canvas_W = FigureCanvasTkAgg(self.figW, master=self)
		self.canvas_W.draw()
		self.canvas_W.get_tk_widget().grid(row=9,column=1,rowspan=20,columnspan=6)
		self.frameslider = Scale(self, from_=0, to=1, orient=HORIZONTAL)
		self.frameslider.grid(row=29, column=1, columnspan=3, sticky='EW')

		self.update()

if __name__ == "__main__":
	MainWindow = App_Window(None)
	MainWindow.mainloop()