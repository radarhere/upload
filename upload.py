import tkinter
import tkinter.messagebox
from tkinter import ttk
import os, sys, re, subprocess, webbrowser
from mutagen.mp3 import MP3

from windows import about
from util import progress, webApi

class Upload:
	uploadInProgress = False
	version = '1.1'

	successfulCheckURL = None

	def getPath(self):
		dir = os.path.expanduser('~/Music/iTunes/iTunes Media/Music')
		mostRecent = 0
		mostRecentPath = None
		for path, dirs, files in os.walk(dir):
			for file in files:
				if not file.startswith('.') and os.path.splitext(file)[1] == '.mp3':
					absolutePath = os.path.join(path, file)
					modificationTime = os.path.getmtime(absolutePath)
					if modificationTime > mostRecent:
						mostRecent = modificationTime
						mostRecentPath = absolutePath
		if mostRecentPath != None:
			return mostRecentPath

	def convert(self, path, dest):
		for lame in ['/opt/local/bin/lame', '/usr/local/bin/lame']:
			if os.path.exists(lame):
				p = subprocess.Popen([lame,'-m','m',path,dest], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				break
		else:
			tkinter.messagebox.showerror("Error", "LAME could not be found.")
			return
		
		re_compile = re.compile(b"[0-9]+/[0-9]+")
		while True:
			line = p.stdout.readline()
			if not line:
				break
			groups = re_compile.search(line)
			if groups:
				progress, total = groups.group(0).split(b"/")
				self.progressbar.update(float(progress) / int(total))

	def getSermonDetails(self):
		path = self.getPath()
		if not path:
			tkinter.messagebox.showerror("Error", "An error occurred in connecting to iTunes.")
			sys.exit()

		audio = MP3(path)

		title = str(audio['TIT2']) if 'TIT2' in audio else ''
		artist = str(audio['TPE1']) if 'TPE1' in audio else ''
		comments = ''
		for k, v in audio.items():
			if k.startswith('COMM:'):
				comments = str(v)
				break

		self.originalPath = path
		
		return title, artist, comments

	def go(self):
		title = self.titleEntry.get()
		speaker = self.speakerEntry.get()
		readings = self.readingsEntry.get()
		if not title:
			tkinter.messagebox.showerror("Error", "You must enter a title.")
			return
		if not speaker:
			tkinter.messagebox.showerror("Error", "You must enter a speaker.")
			return
		if not readings:
			tkinter.messagebox.showerror("Error", "You must enter readings.")
			return

		self.uploadButton.config(state=tkinter.DISABLED)

		self.uploadInProgress = True
		
		dest = os.path.join(self.resourcesPath, os.path.basename(self.originalPath))
		
		self.stateLabel.config(text="Converting...")
		self.convert(self.originalPath, dest)
		
		self.stateLabel.config(text="Uploading...")
		self.webConnection = webApi.webApi(self, dest, self.progressbar)
		self.webConnection.uploadFile(title, speaker, readings)
		os.remove(dest)
		
		self.stateLabel.config(text="Ready To Upload")
		self.uploadButton.config(state=tkinter.NORMAL)
		self.progressbar.update(0)
		
		if self.successfulCheckURL:
			#Open the page in a browser, so that the user can verify that all was successful
			webbrowser.open(self.successfulCheckURL)

	def frozen(self):
		return hasattr(sys, "frozen")

	def quit(self):
		self.root.destroy()

	def centreWindow(self):
		width, height = self.root.geometry().split('+')[0].split('x')
		x = str(int(self.root.winfo_screenwidth() / 2 - int(width) / 2))
		y = str(int(self.root.winfo_screenheight() / 2 - int(height) / 2))
		self.root.geometry(width + 'x' + height + '+' + x + '+' + y)

	def __init__(self):
		self.root = root = tkinter.Tk()

		root.resizable(width=False,height=False)
		root.title("Upload")

		self.frame = frame = ttk.Frame(root)

		ttk.Label(frame, text = "Title").grid(row=0,column=0,sticky=tkinter.W,padx=5,pady=5)
		ttk.Label(frame, text = "Speaker").grid(row=1,column=0,sticky=tkinter.W,padx=5,pady=5)
		ttk.Label(frame, text = "Readings").grid(row=2,column=0,sticky=tkinter.W,padx=5,pady=5)
		ttk.Label(frame, text = "Sermon").grid(row=3,column=0,sticky=tkinter.W,padx=5,pady=5)

		localpath = sys.path[0].replace('/lib/python'+str(sys.version_info.major)+str(sys.version_info.minor)+'.zip','')
		self.resourcesPath = os.path.join(localpath, 'resources')
		for filename in os.listdir(self.resourcesPath):
			if filename.endswith('.mp3'):
				os.remove(os.path.join(self.resourcesPath, filename))
		title, artist, comments = self.getSermonDetails()

		self.titleEntry = ttk.Entry(frame, width=30)
		self.titleEntry.insert(0, title)
		self.titleEntry.grid(row=0,column=1,padx=5,pady=5)

		self.speakerEntry = ttk.Entry(frame, width=30)
		self.speakerEntry.insert(0, artist)
		self.speakerEntry.grid(row=1,column=1,padx=5,pady=5)

		self.readingsEntry = ttk.Entry(frame, width=30)
		self.readingsEntry.insert(0, comments)
		self.readingsEntry.grid(row=2,column=1,padx=5,pady=5)

		self.progressbar = progress.Progress(frame)
		
		sermonText = os.path.basename(self.originalPath)
		ttk.Label(frame, text = sermonText, anchor=tkinter.CENTER).grid(row=5,column=0,columnspan=2,padx=5,pady=5)

		self.stateLabel = ttk.Label(frame, text = "Ready To Upload", anchor=tkinter.CENTER)
		self.stateLabel.grid(row=6,column=0,columnspan=2,sticky=tkinter.W+tkinter.E,padx=30,pady=10)

		self.progressbar.getItem().grid(row=7,column=0,columnspan=2,sticky=tkinter.W+tkinter.E,padx=30,pady=10)

		self.uploadButton = ttk.Button(frame, padding=6, takefocus=0, text = "Upload", command = self.go)
		self.uploadButton.grid(row=8,column=0,columnspan=2,pady=5)

		frame.pack()

		menubar = tkinter.Menu(self.root)
		apple = tkinter.Menu(menubar, name='apple')
		apple.add_command(label="About Upload", command=lambda: about.About(self.resourcesPath, self.version))
		menubar.add_cascade(menu=apple)
		self.root.config(menu=menubar)

		root.update_idletasks()
		self.centreWindow()

		self.root.protocol("WM_DELETE_WINDOW",self.quit)
		self.root.createcommand("exit",self.quit)

		root.mainloop()

if __name__ == '__main__':
	Upload()
