from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2, cookielib

from fileApi import Progress, file_with_callback

class webApi():
	formDestinationURL = None
	uploadDestinationURL = None
	
	#Fields that the form would submit
	postFields = {
		'username': None,
		'password': None
	}
	
	#A segment of code to look for in the response page, to verify whether or not login was successful
	keyLoginPhrase = None

	def __init__(self, itunesPath, progressbar):
		progress = Progress(progressbar)
		self.stream = file_with_callback(itunesPath, 'rb', progress.update, itunesPath)

		jar = cookielib.CookieJar()

		opener = register_openers()
		opener.add_handler(urllib2.HTTPCookieProcessor(jar))

	def login(self):
		if not self.formDestinationURL:
			return
		
		datagen, headers = multipart_encode(self.postFields)
		try:
			request = urllib2.Request(self.formDestinationURL, datagen, headers)
			response = urllib2.urlopen(request)
			success = not self.keyLoginPhrase or self.keyLoginPhrase in response.read()
			
			return success
		except:
			pass

	def uploadFile(self, title, speaker, reading):
		if not self.uploadDestinationURL:
			return
		
		datagen, headers = multipart_encode({"title":title,"speaker":speaker,"readings":reading,"upload":"Upload","sermon": self.stream})
		try:
			request = urllib2.Request(self.uploadDestinationURL, datagen, headers)
			urllib2.urlopen(request)
		except:
			pass