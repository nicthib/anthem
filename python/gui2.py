from main import *
def donothing():
	pass

def jet(dz):
    tmp = cm.jet(plt.Normalize(0,dz-1)(range(dz)))
    return tmp[:,:-1]

def refreshH(self):
	self.lineH = self.Hax1.plot(self.H.T,linewidth=.5)
	ax = self.canvas_H.figure.axes[0]	
	ax.set_xlim(0, len(self.H.T))
	ax.set_ylim(np.min(self.H), np.max(self.H)) 
	self.imH = self.Hax2.imshow(self.H)
	self.imH.axes.set_aspect('auto')
	self.canvas_H.draw()
	return self

def refreshW(self):
	cmap = jet(len(self.H))
	sc = 256/self.brightness
	self.imWH = self.Wax1.imshow((self.W@np.diag(self.H[:,self.framenum])@cmap*sc).reshape(self.ss[0],self.ss[1],3).astype(int))
	self.imWH.axes.set_aspect('equal')
	self.imW = self.Wax2.imshow((self.W@cmap).reshape(self.ss[0],self.ss[1],3))
	self.imW.axes.set_aspect('equal')
	self.canvas_W.draw()
	plt.tight_layout()
	return self

def loadfrommat(self):
	vp = Toplevel(self)
	#vp = Tk()
	file = fd.askopenfilename(title='Select .mat file for import',filetypes=[('.mat files','*.mat')])
	if not file:
		vp.destroy()
		return None, None, None
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
	Button(vp,text='Done',command=vp.quit,width=10).grid(row=2,column=0,columnspan=3)
	vp.mainloop()
	dh = loadmat(file)
	self.H, self.W = dh[varH.get()], dh[varW.get()]
	self.ss = self.W.shape
	self.W = self.W.reshape(self.W.shape[0]*self.W.shape[1],self.W.shape[2])
	self.framenum = 1
	self.brightness=np.max(self.H)
	#return dh[varH.get()]
	self = refreshH(self)
	self = refreshW(self)

class App_Window(Tk):
	def __init__(self,parent):
		Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()
	def initialize(self):
		# Labels
		Label(text='').grid(row=0,column=0)
		Label(text='Input File').grid(row=1, column=1,columnspan=2,sticky='W')
		Label(text='demo1.mat').grid(row=2, column=1,columnspan=2,sticky='W')
		Label(text='Output').grid(row=3, column=1,columnspan=2,sticky='W')
		Label(text='Output save path').grid(row=5, column=1,columnspan=2,sticky='W')
		Label(text='/Users/Nic/Desktop').grid(row=6, column=1,columnspan=2,sticky='W')
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
		st = Label(text='Status:').grid(row=8, column=1,columnspan=6, sticky='W')
		#Label(text='Components to show').grid(row=108, column=5)

		# Entries
		self.filename = Entry(text='').grid(row=4, column=1,columnspan=2,sticky='W')
		self.fr = Entry(textvariable='',width=5).grid(row=1, column=4, sticky='W')
		self.st_p = Entry(text='0',width=5).grid(row=2, column=4, sticky='W')
		self.en_p = Entry(text='100',width=5).grid(row=3, column=4, sticky='W')
		self.baseline = Entry(text='0',width=5).grid(row=4, column=4, sticky='W')
		self.filterH = Entry(text='',width=5).grid(row=5, column=4, sticky='W')
		self.brightness = Entry(text='',width=5).grid(row=6, column=4, sticky='W')
		self.thresh = Entry(text='',width=5).grid(row=1, column=6, sticky='W')
		#self.Wshow = Entry(text='',width=5).grid(row=109, column=4, columnspan=3)

		# Buttons
		Button(text='Edit save path',width=20).grid(row=7, column=1,columnspan=2)
		Button(text='Play Notes',width=20).grid(row=6, column=5,columnspan=2)

		## OPTIONS
		oct_opts = ['0','1','2','3','4','5']
		scale_opts = ['Chromatic (12 notes/oct)','Major Scale (7 notes/oct)','Minor Scale (7 notes/oct)', 
		'Maj. triad (3 notes/oct)','Min. triad (3 notes/oct)','Aug. Triad (3 notes/oct)',
		'Dim. Triad (3 notes/oct)','Maj. Sixth (4 notes/oct)','Min. Sixth (4 notes/oct)',
		'Maj. Seventh (4 notes/oct)','Min. Seventh (4 notes/oct)','Aug. Seventh (4 notes/oct)',
		'Dim. Seventh (4 notes/oct)','Maj. 7th add9 (5 notes/oct)','Min. 7th add9 (5 notes/oct)']
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

		loadarg = partial(loadfrommat, self)

		# Menu bar
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Load from .mat", command=loadarg)
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

		# Plot H
		self.figH = plt.Figure(figsize=(6,6), dpi=100)
		self.Hax1 = self.figH.add_subplot(211)
		self.Hax2 = self.figH.add_subplot(212)
		x,y = [],[]
		self.lineH = self.Hax1.plot(x,y,'r-')
		self.Hax1.set_title('Raw Temporal Data (H)')
		self.Hax2.set_title('Converted Temporal Data (H\')')
		self.Hax1.axis('off')
		self.Hax2.axis('off')
		self.canvas_H = FigureCanvasTkAgg(self.figH, master=self)
		self.canvas_H.draw()
		self.canvas_H.get_tk_widget().grid(row=1,column=7,rowspan=100,columnspan=1)

		# Plot W
		self.figW = plt.Figure(figsize=(6,2), dpi=100)
		self.Wax1 = self.figW.add_subplot(121)
		self.Wax2 = self.figW.add_subplot(122)
		self.Wax1.set_title('Output(H x W)')
		self.Wax2.set_title('Spatial Components (W)')
		self.Wax1.axis('off')
		self.Wax2.axis('off')
		self.canvas_W = FigureCanvasTkAgg(self.figW, master=self)
		self.canvas_W.draw()
		self.canvas_W.get_tk_widget().grid(row=9,column=1,rowspan=100,columnspan=6)
		self.update()

if __name__ == "__main__":
	MainWindow = App_Window(None)
	MainWindow.mainloop()