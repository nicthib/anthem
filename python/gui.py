from main import *
global w
w = Tk()
H = []
W = []

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
Label(text='Components to show').grid(row=108, column=5)

# Entries
filename = Entry(text='').grid(row=4, column=1,columnspan=2,sticky='W')
fr = Entry(textvariable='',width=5).grid(row=1, column=4, sticky='W')
st_p = Entry(text='0',width=5).grid(row=2, column=4, sticky='W')
en_p = Entry(text='100',width=5).grid(row=3, column=4, sticky='W')
baseline = Entry(text='0',width=5).grid(row=4, column=4, sticky='W')
filterH = Entry(text='',width=5).grid(row=5, column=4, sticky='W')
brightness = Entry(text='',width=5).grid(row=6, column=4, sticky='W')
thresh = Entry(text='',width=5).grid(row=1, column=6, sticky='W')
Wshow = Entry(text='',width=5).grid(row=109, column=4, columnspan=3)

# Buttons
Button(text='Edit save path',width=20).grid(row=7, column=1,columnspan=2)
Button(text='Play Notes',width=20).grid(row=6, column=5,columnspan=2)

# Plot W
figure = plt.Figure(figsize=(6,2), dpi=100)
ax1 = figure.add_subplot(121)
ax2 = figure.add_subplot(122)
ax1.set_title('Output(H x W)')
ax2.set_title('Spatial Components (W)')
ax1.axis('off')
ax2.axis('off')

chart_type = FigureCanvasTkAgg(figure, w)
chart_type.get_tk_widget().grid(row=9,column=1,rowspan=100,columnspan=6)
plt.tight_layout()

# Plot H
figure = plt.Figure(figsize=(6,6), dpi=100)
ax3 = figure.add_subplot(211)
ax4 = figure.add_subplot(212)
ax3.set_title('Raw Temporal Data (H)')
ax4.set_title('Converted Temporal Data (H\')')
chart_type = FigureCanvasTkAgg(figure, w)
chart_type.get_tk_widget().grid(row=1,column=7,rowspan=100,columnspan=1)
plt.tight_layout()

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
var = StringVar(w)
var.set('0')
oct_add = OptionMenu(w,var,*oct_opts).grid(row=2, column=6, sticky='W')
var = StringVar(w)
var.set('Chromatic')
scaletype = OptionMenu(w,var,*scale_opts).grid(row=3, column=6, sticky='W')
var = StringVar(w)
var.set('C')
scaletype = OptionMenu(w,var,*key_opts).grid(row=4, column=6, sticky='W')
var = StringVar(w)
var.set('Stream')
audio_fmt = OptionMenu(w,var,*fmt_opts).grid(row=5, column=6, sticky='W')

# Functions
def donothing():
	pass

def updateplots():
	print('trying...')
	plt.sca(ax3)
	plt.plot(H.flatten(1))

def loadfrommat(w):
	vp = Toplevel(w)
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
	Button(vp,text='Done',command=vp.destroy,width=10).grid(row=2,column=0,columnspan=3)
	vp.mainloop()
	dh = loadmat(file)
	global H, W
	H, W = dh[varH.get()], dh[varW.get()]
	updateplots()

loadarg = partial(loadfrommat, w)

# Menu bar
menubar = Menu(w)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load from .mat", command=loadarg)
filemenu.add_command(label="Load from config", command=donothing)
filemenu.add_command(label="Quit", command=w.quit)

savemenu = Menu(menubar, tearoff=0)
savemenu.add_command(label="Audio", command=donothing)
savemenu.add_command(label="Video", command=donothing)
savemenu.add_command(label="Combine A/V", command=donothing)
savemenu.add_command(label="Config File", command=donothing)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Save", menu=savemenu)
w.config(menu=menubar)

# Seperators
ttk.Separator(w, orient='vertical').grid(column=0, row=1, rowspan=8, sticky='nse')
ttk.Separator(w, orient='vertical').grid(column=2, row=1, rowspan=7, sticky='nse')
ttk.Separator(w, orient='vertical').grid(column=4, row=1, rowspan=7, sticky='nse')
ttk.Separator(w, orient='vertical').grid(column=6, row=1, rowspan=8, sticky='nse')
ttk.Separator(w, orient='horizontal').grid(column=1, row=1, columnspan=6,sticky='nwe')
ttk.Separator(w, orient='horizontal').grid(column=1, row=7, columnspan=6,sticky='swe')
ttk.Separator(w, orient='horizontal').grid(column=1, row=8, columnspan=6,sticky='swe')

w.mainloop()