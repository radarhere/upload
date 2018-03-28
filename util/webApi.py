import requests, json
from requests_toolbelt.multipart import encoder

import os

class webApi:
	uploadURL = None

	def __init__(self, parent, itunesPath, progressbar):
		self.parent = parent
		self.path = itunesPath
		self.callback = progressbar.update

	def monitor_callback(self, monitor):
		self.callback(monitor.bytes_read / monitor.len)

	def uploadFile(self, title, speaker, reading):
		title = title.strip()
		speaker = speaker.strip()
		reading = reading.strip()

		with open(self.path, 'rb') as f:
			try:
				e = encoder.MultipartEncoder(fields={
					"title":title,
					"speaker":speaker,
					"readings":reading,
					"sermon":(os.path.basename(self.path), f, 'audio/mpeg')
				})
				m = encoder.MultipartEncoderMonitor(e, self.monitor_callback)
				requests.post(self.uploadURL, data=m, headers={
					'Content-Type': m.content_type
				})
			except:
				if not self.parent.frozen():
					raise