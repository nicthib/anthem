from tkinter import *
from tkinter.ttk import Progressbar, Separator, Combobox

def init_entry(fn):
	if isinstance(fn, str):
		entry = StringVar()
	else:
		entry = DoubleVar()
	entry.set(fn)
	return entry

class GUI(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.cmaps = tuple(sorted(['viridis', 'plasma', 'inferno', 'magma', 'cividis','binary', 
		'bone', 'pink','spring', 'summer', 'autumn', 'winter', 'cool','hot','copper','Spectral', 
		'coolwarm', 'bwr', 'seismic','twilight', 'hsv', 'Paired', 'prism', 'ocean', 
		'terrain','brg', 'rainbow', 'jet'],key=lambda s: s.lower()))
		self.cmapchoice=init_entry('jet')
		self.cmapchooser = Combobox(self,textvariable=self.cmapchoice,width=7)
		self.cmapchooser['values'] = self.cmaps
		self.option_add('*TCombobox*Listbox.fieldbackground', 'red')
		self.cmapchooser.grid(row=6, column=4, sticky='WE')
		self.cmapchooser.current()



if __name__ == "__main__":
	MainWindow = GUI()
	MainWindow.mainloop()