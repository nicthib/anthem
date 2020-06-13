from tkinter import *

class App_Window(Tk):
	def __init__(self,parent):
		Tk.__init__(self,parent)
		self.parent=parent

		self.label=Label(self)
		self.label.pack()

		self.slider=Scale(self, from_=0, to=100, orient=HORIZONTAL)
		self.slider['command'] = self.sliderfun
		self.slider.pack()

	
	def sliderfun(self,event):
		self.label['text'] = 'Slider = {}'.format(self.slider.get())
		self.update_idletasks()

if __name__ == "__main__":
	MainWindow = App_Window(None)
	MainWindow.mainloop()