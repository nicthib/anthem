from main import *
def donothing():
	pass

def jet(dz):
	tmp = cm.jet(plt.Normalize(0,dz-1)(range(dz)))
	return tmp[:,:-1]

def init_entry(fn):
	if isinstance(fn, str):
		entry = StringVar()
	else:
		entry = DoubleVar()
	entry.set(fn)
	return entry

class App_Window(Tk):
	def __init__(self,parent):
		Tk.__init__(self,parent)
		self.parent = parent
		self.init_fields()

	def loadfrommat(self):
		vp = Toplevel(self)
		file = fd.askopenfilename(title='Select .mat file for import',filetypes=[('.mat files','*.mat')])
		if not file:
			vp.destroy()
			return None, None, None
		vp.attributes("-topmost", True)
		vs = whosmat(file)
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
		dh = loadmat(file)
		self.H, self.W = dh[varH.get()], dh[varW.get()]
		self.ss = self.W.shape
		self.W = self.W.reshape(self.W.shape[0]*self.W.shape[1],self.W.shape[2])
		self.framenum = 1
		self.brightness.set(f'{float(f"{np.max(self.H):.3g}"):g}')
		self.filein.set(file.split('/')[-1])
		self.fileout.set(file.split('/')[-1])
		self.savepath.set(__file__)
		self.init_plots()
		self.refreshH()
		self.refreshW()

	def refreshH(self):
		self.init_plots()
		self.H_p = self.H[:,int(len(self.H.T)*self.st_p.get()/100):int(len(self.H.T)*self.en_p.get()/100)] + self.baseline.get()
		self.lineH = self.Hax1.plot(self.H_p.T,linewidth=.5)
		ax = self.canvas_H.figure.axes[0]	
		ax.set_xlim(0, len(self.H_p.T))
		ax.set_ylim(np.min(self.H_p), np.max(self.H_p)) 
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		self.imH = self.Hax2.imshow(self.H_p)
		self.imH.axes.set_aspect('auto')
		self.canvas_H.draw()

	def refreshW(self):
		self.cmap = jet(len(self.H))
		self.sc = 255/self.brightness.get()
		self.imWH = self.Wax1.imshow((self.W@np.diag(self.H_p[:,self.framenum])@self.cmap*self.sc).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.imWH.axes.set_aspect('equal')
		self.imW = self.Wax2.imshow((self.W@self.cmap*255/np.max(self.W)).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.imW.axes.set_aspect('equal')
		self.canvas_W.draw()

		# Update slider max min
		self.frameslider['to'] = int(len(self.H_p.T)-1)
		self.frameslider['command'] = self.refreshW_slider
		plt.tight_layout()

	def refreshW_slider(self,event):
		self.imWH.remove()
		self.imWH = self.Wax1.imshow((self.W@np.diag(self.H_p[:,self.frameslider.get()])@self.cmap*self.sc).reshape(self.ss[0],self.ss[1],3).clip(min=0,max=255).astype('uint8'))
		self.canvas_W.draw()

	def init_fields(self):
		# StringVars
		self.filein=init_entry('...')
		self.fileout=init_entry('...')
		self.savepath=init_entry('...')
		self.fr=init_entry('10')
		self.st_p=init_entry(0)
		self.en_p=init_entry(100)
		self.baseline=init_entry(0)
		self.filterH=init_entry(0)
		self.brightness=init_entry(0)
		self.thresh=init_entry(0)

		# Labels
		Label(text='').grid(row=0,column=0)
		Label(text='Input File').grid(row=1, column=1,columnspan=2,sticky='W')
		Label(textvariable=self.filein).grid(row=2, column=1,columnspan=2,sticky='W')
		Label(text='Output').grid(row=3, column=1,columnspan=2,sticky='W')
		Label(text='Output save path').grid(row=5, column=1,columnspan=2,sticky='W')
		Label(textvariable=self.savepath).grid(row=6, column=1,columnspan=2,sticky='W')
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
		Entry(textvariable=self.fr,width=5).grid(row=1, column=4, sticky='W')
		Entry(textvariable=self.st_p,width=5).grid(row=2, column=4, sticky='W')
		Entry(textvariable=self.en_p,width=5).grid(row=3, column=4, sticky='W')
		Entry(textvariable=self.baseline,width=5).grid(row=4, column=4, sticky='W')
		Entry(textvariable=self.filterH,width=5).grid(row=5, column=4, sticky='W')
		Entry(textvariable=self.brightness,width=5).grid(row=6, column=4, sticky='W')
		Entry(textvariable=self.thresh,width=5).grid(row=1, column=6, sticky='W')
		#self.Wshow = Entry(text='',width=5).grid(row=109, column=4, columnspan=3)

		# Buttons
		Button(text='Edit save path',width=20).grid(row=7, column=1,columnspan=2)
		Button(text='Play Notes',width=20).grid(row=6, column=5,columnspan=2)
		Button(text='Update',command=lambda:[self.refreshH(),self.refreshW()]).grid(row=8, column=5,columnspan=2,sticky='WE')

		# Options
		oct_opts = ['0','1','2','3','4','5']
		scale_opts = ['Chromatic (12/oct)','Major scale (7/oct)','Minor scale (7/oct)', 
		'Maj. triad (3/oct)','Min. triad (3/oct)','Aug. triad (3/oct)',
		'Dim. triad (3/oct)','Maj. 6th (4/oct)','Min. 6th (4/oct)',
		'Maj. 7th (4/oct)','Min. 7th (4/oct)','Aug. 7th (4/oct)',
		'Dim. 7th (4/oct)','Maj. 7/9 (5/oct)','Min. 7/9 (5/oct)']
		key_opts = ['C','C#/D♭','D','D#/E♭','E','F','F#/G♭','G','G#/A♭','A','A#/B♭','B']
		fmt_opts = ['Stream','Dynamic','MIDI']

		# Option Menus
		var = StringVar(self)
		var.set('0')
		oct_add = OptionMenu(self,var,*oct_opts).grid(row=2, column=6, sticky='W')
		var = StringVar(self)
		var.set('Chromatic')
		scaletype = OptionMenu(self,var,*scale_opts).grid(row=3, column=6, sticky='W')
		var = StringVar(self)
		var.set('C')
		scaletype = OptionMenu(self,var,*key_opts).grid(row=4, column=6, sticky='W')
		var = StringVar(self)
		var.set('Stream')
		audio_fmt = OptionMenu(self,var,*fmt_opts).grid(row=5, column=6, sticky='W')

		# Menu bar
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Load from .mat", command=self.loadfrommat)
		filemenu.add_command(label="Load from config", command=donothing)
		filemenu.add_command(label="Quit", command=self.quit)

		savemenu = Menu(menubar, tearoff=0)
		savemenu.add_command(label="Audio", command=donothing)
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
		ttk.Separator(self, orient='horizontal').grid(column=1, row=1, columnspan=6,sticky='nwe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=7, columnspan=6,sticky='swe')
		ttk.Separator(self, orient='horizontal').grid(column=1, row=8, columnspan=6,sticky='swe')
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