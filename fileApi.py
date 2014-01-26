import os
import Tkinter, ttk

#Modified from http://stackoverflow.com/questions/5925028/urllib2-post-progress-monitoring
class Progress(object):
	def __init__(self, frame):
		self._progressbar = ttk.Progressbar(self.frame, maximum = 100)
		
		self._seen = 0.0

	def getItem(self):
		return self._progressbar

	def update(self, total, size, name):
		self._seen += size
		percent = (self._seen / total) * 100.0
		
		#While the Tkinter API would suggest that you use .step(),
		#in what I presume is a bug in ttk,
		#the final step() does not take you to 100%, but back to 0%
		
		#So this is a workaround
		self.progressbar.config(value=int(percent))
		self.progressbar.update()

class file_with_callback(file):
	def __init__(self, path, mode, callback, *args):
		file.__init__(self, path, mode)
		self.seek(0, os.SEEK_END)
		
		self._total = self.tell()
		self.seek(0)
		
		self._callback = callback
		self._args = args

	def __len__(self):
		return self._total

	def read(self, size):
		data = file.read(self, size)
		self._callback(self._total, len(data), *self._args)
		return data