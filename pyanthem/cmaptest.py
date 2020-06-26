from tkinter import *

class GUI(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.initGUI()

	def initGUI(self):
		self.cmapchoice = StringVar()
		self.cmapchoice.set('jet')
		self.cmaps = sorted(['viridis', 'plasma', 'inferno', 'magma','binary', 
			'bone','spring', 'summer', 'autumn', 'winter', 'cool','hot','copper','Spectral', 
			'coolwarm', 'bwr', 'seismic','twilight', 'hsv', 'Paired', 'Accent', 'prism', 'ocean', 
			'terrain','brg', 'rainbow', 'jet'],key=lambda s: s.lower())
		for i in range(7): # Some empty rows with other widgets
			Label(self,text='OTHER WIDGETS').grid(row=i, column=1, sticky='WE')
		OptionMenu(self,self.cmapchoice,*self.cmaps).grid(row=9, column=1, sticky='WE')

if __name__ == "__main__":
	MainWindow = GUI()
	MainWindow.mainloop()
