import Tkinter, ttk, tkMessageBox
import os, sys, re, urllib

import aboutme
from webApi import webApi

class Upload:
	uploadInProgress = False
	fileReady = False
	version = '1.0'

	fields = ["Title", "Speaker", "Readings", "Sermon"]
	
	successfulCheckURL = None
	
	script = """set itunesWasOpen to appIsRunning("iTunes")

tell application "iTunes"
	set difference to 77744011
	repeat with theTrack in every track
		set thisDifference to ((current date) - (date added of theTrack))
		if (thisDifference < difference and bit rate of theTrack is not 64) then
			set difference to thisDifference
			set mostRecentTrack to theTrack
		end if
	end repeat
	set newTrack to item 1 of (convert mostRecentTrack)
	
	set titleName to name of newTrack
	set artistName to artist of newTrack
	set commentsName to comment of newTrack
	
	set newTrackPathOne to location of newTrack
	set newTrackPath to POSIX path of newTrackPathOne
	
	delete newTrack
	
	set x to {titleName, artistName, commentsName, newTrackPath}
	set text item delimiters of AppleScript to "|"
	get x as string
end tell

on appIsRunning(appName)
	tell application "System Events" to (name of processes) contains appName
end appIsRunning"""

	#Menu system
	def aboutme(self):
		aboutme.AboutMe(self.version)

	def createMenu(self):
		menubar = Tkinter.Menu(self.root)
		apple = Tkinter.Menu(menubar, name='apple')
		apple.add_command(label="About Upload", command=self.aboutme)
		menubar.add_cascade(menu=apple)
		self.root.config(menu=menubar)

	#iTunes interactions
	def getSermonPath(self):
		self.fileReady = True

		fout = os.popen("osascript -e '" + self.script + "'")
		applescriptResponse = fout.read()
		if applescriptResponse:
			if applescriptResponse.endswith('\n'):
				applescriptResponse = applescriptResponse[:-1]
			
			self.data = {}
			self.data['Title'], self.data['Speaker'], self.data['Readings'], self.sermonPath = applescriptResponse.split('|')
			
			self.setupTextFields()
		else:
			self.messageLabel.config(text="An error occurred with iTunes.")
		
	#Begin upload
	def beginUpload(self):
		title = self.titleEntry.get()
		speaker = self.speakerEntry.get()
		readings = self.readingsEntry.get()
		if title == "":
			tkMessageBox.showerror("Error","You must enter a title.")
			return
		if speaker == "":
			tkMessageBox.showerror("Error","You must enter a speaker.")
			return
		if readings == "":
			tkMessageBox.showerror("Error","You must enter readings.")
			return

		self.uploadButton.config(state=Tkinter.DISABLED)

		self.uploadInProgress = True
		
		webConnection = webApi(self.sermonPath, self.progressbar)
		if webConnection.login():
			webConnection.uploadFile(title, speaker, readings)
		
		self.uploadButton.config(state=Tkinter.NORMAL)
		self.progressbar.update(0)
		
		if self.successfulCheckURL:
			#Open the page in a browser, so that the user can verify that all was successful
			os.system("open "+self.successfulCheckURL)

	#Window manipulation
	def setupTextFields(self):
		self.messageLabel.grid_forget()
		
		for i in range(0, len(self.fields)):
			ttk.Label(self.frame, text = self.fields[i]).grid(row=i,column=0,sticky=Tkinter.W,padx=5,pady=5)

		#Sermon titles are typically formatted 'YYYY.MM.DD [AP]M Title'
		#Since the upload form only requires the title, the rest of the data can be removed
		self.data['Title'] = re.sub(r'[0-9]{4}.[0-9]{2}.[0-9]{2} [AP]M ','',self.data['Title'])

		self.entries = {}
		#Entry fields for Title, Speaker and Readings
		for i in range(0, len(self.fields)-1):
			fieldKey = self.fields[i]
			
			entryField = ttk.Entry(self.frame, width=20)
			entryField.insert(0, self.data[fieldKey])
			entryField.grid(row=i,column=1,padx=5,pady=5)
			
			self.entries[fieldKey] = entryField

		sermonText = self.sermonPath.split('/')[-1]
		self.sermonLabel = ttk.Label(self.frame, text = sermonText)
		self.sermonLabel.grid(row=3,column=1,padx=5,pady=5)

		self.progressbar = ttk.Progressbar(self.frame, maximum = 100)
		self.progressbar.grid(row=4,column=0,columnspan=2,sticky=Tkinter.W+Tkinter.E,padx=20,pady=10)

		self.uploadButton = ttk.Button(self.frame, padding=6, takefocus=0, text = "Upload", command = self.beginUpload)
		self.uploadButton.grid(row=5,column=0,columnspan=2,pady=5)

	def centreWindow(self, specifiedWidth=None):
		self.root.update_idletasks()
		
		width, height = self.root.geometry().split('+')[0].split('x')
		if specifiedWidth != None:
			width = specifiedWidth
		
		self.root.geometry(str(width) + 'x' + str(height) + '+' + str(self.root.winfo_screenwidth() / 2 - int(width) / 2) + '+' + str(self.root.winfo_screenheight() / 2 - int(height) / 2))

	def quit(self):
		if self.fileReady:
			os.remove(self.sermonPath)
		self.root.destroy()

	def __init__(self):
		self.root = Tkinter.Tk()

		self.root.resizable(width=False,height=False)
		self.root.title("Upload")
		self.root.config(background="#eee")

		self.frame = ttk.Frame(self.root)
		self.messageLabel = ttk.Label(self.frame, text = "Waiting for iTunes to finish converting")
		self.messageLabel.grid(row=0,column=0,padx=25,pady=100)
		self.frame.pack()
		
		self.centreWindow()

		self.createMenu()

		self.root.protocol("WM_DELETE_WINDOW",self.quit)
		self.root.createcommand("exit",self.quit)
		
		#Start iTunes conversion on another the main thread
		self.root.after(1000, self.getSermonPath)
		
		self.root.mainloop()

if __name__ == '__main__':
	Upload()