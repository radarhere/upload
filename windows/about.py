import tkinter, os, sys
from PIL import Image, ImageTk

class About:
	def __init__(self, resourcesPath, version):
		self.root = tkinter.Toplevel()
		
		#Text strings
		textArray = ['Created by Radartech','www.radartech.com.au','Version: '+version]
		for i in range(0,len(textArray)):
			textString = textArray[i]
			
			tkinter.Label(self.root, text=textString).grid(row=1,column=i)

		#Image label
		im = Image.open(os.path.join(resourcesPath, 'About.jpg'))

		self.photoImage = ImageTk.PhotoImage(im)
		self.label = tkinter.Label(self.root, image=self.photoImage)
		self.label.grid(row=0,column=0,columnspan=3)

		#Set size of window and centre it on the screen
		width = im.size[0]
		height = im.size[1] + 26
		
		x = int(self.root.winfo_screenwidth() / 2 - width / 2)
		y = int(self.root.winfo_screenheight() / 2 - height / 2)
		self.root.geometry(str(width) + 'x' + str(height) + '+' + str(x) + '+' + str(y))
		
		self.root.update_idletasks()

		#Bindings
		self.root.bind('<Button-1>',self.close)

	def close(self, event):
		self.root.destroy()