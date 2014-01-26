import Tkinter, Image, ImageTk
import sys

class AboutMe:
	def __init__(self, version):
		self.root = Tkinter.Toplevel()
		
		#No border
		self.root.overrideredirect(True)

		#Text strings
		textArray = ['Created by Radartech','www.radartech.com.au','Version: '+version]
		for i in range(0,len(textArray)):
			textString = textArray[i]
			
			Tkinter.Label(self.root, text=textString).grid(row=1,column=i)

		#Image label
		aboutImage = Image.open(sys.path[0] + '/resources/About.jpg')

		self.photoImage = ImageTk.PhotoImage(aboutImage)
		self.label = Tkinter.Label(self.root, image=self.photoImage)
		self.label.grid(row=0,column=0,columnspan=3)

		#Set size of window and centre it on the screen
		imageSize = aboutImage.size
		
		width = imageSize[0]
		height = imageSize[1] + 26
		x = self.root.winfo_screenwidth() / 2 - width / 2
		y = self.root.winfo_screenheight() / 2 - height / 2
		
		self.root.geometry(str(width) + 'x' + str(height) + '+' + str(x) + '+' + str(y))

		#Bindings
		self.root.bind('<Button-1>',self.close)

	def close(self, event):
		self.root.destroy()