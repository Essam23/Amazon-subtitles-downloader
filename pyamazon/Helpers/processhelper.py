import base64, io, logging, os, subprocess, platform, requests
from pyamazon.Configs.config import Config
from pymp4.parser import Box
from uuid import UUID

class ProcessHelper(object):
	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.aria2c = Config().getConfig()["aria2c"]
		self.mediainfo = Config().getConfig()["mediainfo"]
		self.mkvmerge = Config().getConfig()["mkvmerge"]
		self.mp4decrypt = Config().getConfig()["mp4decrypt"]

	def legacyDownloader(self, url, name):
		self.logger.debug("Downloading: {}".format(os.path.basename(name)))
		response = requests.get(url=url)
		if response.status_code == 200:
			with open(name, "wb") as writer:
				writer.write(response.content)
			return True
		self.logger.warning("unable to download subtitles")
		self.logger.warning(response.text)
		return False

	def downloader(self, urls, output):

		if os.path.exists(output):
		    return

		command = [
			self.aria2c,
			'--continue=true',
			'--enable-color=false',
			'--allow-overwrite=true',
			'--auto-file-renaming=false',
			'--file-allocation=none',
			'--header="Range: bytes=0-"',
			'--header="DNT: 1"',
			'--async-dns=false',
			'--summary-interval=0',
			'--retry-wait=5',
			'--uri-selector=inorder',
			'--console-log-level=warn',
			'--download-result=hide',
			'-x16',
			'-j16',
			'-s16',
			'-d',
			os.path.dirname(output),
			'-o',
			os.path.basename(output)]
		
		for url in urls:
			command.append(url)
			print(url)
		self.logger.debug("Sending Commands to aria2c...")
		self.logger.debug(command)
		try:
			aria = subprocess.call(command)
		except FileNotFoundError as error:
			self.logger.warning("UNABLE TO FIND {}".format(self.aria2c))
			exit(-1)
		if aria != 0:
			raise ValueError("Aria2c exited with code {}".format(aria))

		return

	def aria2c_download(self, command):
		aria2c_command = [self.aria2c]
		aria2c_command.extend(command)
		self.logger.debug(aria2c_command)
		aria2c = subprocess.call(aria2c_command)
		if aria2c != 0:
			raise ValueError("Aria2c exited with code {}".format(aria2c))

	def decrypt(self, encrypted, decrypted, keys):
		self.logger.info("Decrypting: {}".format(os.path.basename(encrypted)))
        
		if os.path.exists(decrypted):
			return

		command = []
		if platform.system() == "Linux":
			command.append("wine")

		command.append(self.mp4decrypt)
		command.append(encrypted)
		command.append(decrypted)
		command.append('--show-progress')
		for key in keys['keys']:
			command.append("--key")
			command.append("{}".format(key))

		self.logger.debug("mp4decrypt command...")
		self.logger.debug(command)
		subprocess.call(command)

		return

	def muxer(self, commands):
		muxer_command = [self.mkvmerge]
		muxer_command.extend(commands)
		self.logger.debug(commands)
		mkvmerge = subprocess.call(muxer_command)
		#if mkvmerge != 0:
			#self.logger.warning("mkvmerge commands:\n{}".format(muxer_command))
			#raise ValueError("mkvmerge exited with error code {}".format(mkvmerge))

	def mediainfo_output(self, file):
		media_commands = [
			self.mediainfo,
			'--Output=XML',
			file
		]

		media_output = subprocess.Popen(media_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		media_output = media_output.stdout.read()
		return media_output.decode("utf-8")

	def getPSSH(self, mp4_file):
		"""
		get the pssh from the mp4 file
		:param mp4_file:
		:return:
		"""
		mp4 = open(mp4_file, "rb")
		mp4.seek(0, io.SEEK_END)
		eof = mp4.tell()
		mp4.seek(0)
		pssh = ""
		while mp4.tell() < eof:
			boxes = Box.parse_stream(mp4)
			if boxes.type == b'moov':
				for box in boxes.children:
					if box.type == b'pssh':
						if box.system_ID == UUID('edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'):
							pssh = base64.b64encode(box.init_data).decode('utf8')
							break
				break
		mp4.close()
		return pssh

	def remove_files(self, name, file):
		for files in os.listdir(os.path.dirname(file)):
			if name in files:
				temp = os.path.join(os.path.dirname(file), files)
				if not temp.endswith("mkv"):
					os.remove(temp)
