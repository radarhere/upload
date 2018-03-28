import tkinter

class Progress:
	def __init__(self, frame):
		self._progressbar = tkinter.ttk.Progressbar(frame, maximum = 100)

	def getItem(self):
		return self._progressbar

	def update(self, progress):
		#While the Tkinter API would suggest that you use .step(),
		#in what I presume is a bug in ttk,
		#the final step() does not take you to 100%, but back to 0%
		
		#So this is a workaround
		self._progressbar.config(value=int(progress * 100))
		self._progressbar.update()