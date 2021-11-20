import json, logging, os, re, requests, sys
from bs4 import BeautifulSoup as Soup, Tag
from pyamazon.Downloader import AmazonDownloader as downloader
from pyamazon.Helpers.requesthelper import RequestHelper
from pyamazon.Params import AmazonParameters
from pyamazon.Configs.Amazon import *
from pyamazon.Configs.config import Config as universal

class Amazon(object):
	def __init__(self, *kwargs):
		self.none_amazon_items = [
			'cloudfront',
			'level3',
			'akamai',
			'limelight',
			'output',
		]
		self.amazon_items = [
			"prime_cookies",
			"prime_cookies_ca",
			"amazon_cookies_us",
			"amazon_cookies_uk",
			"amazon_cookies_de",
			"amazon_cookies_jp",
			"tmdb",
		]
		self.arguments = json.loads(json.dumps(kwargs))[0]
		self.loglevel = (logging.INFO, logging.DEBUG)[self.arguments["debug"] is not False]
		self.asin = (None, self.arguments["asin"])[self.arguments["asin"] is not None]
		self.file = (None, self.arguments["file"])[self.arguments["file"] is not None]
		self.quality = ('best', self.arguments['quality'])[self.arguments['quality'] is not None]
		self.codec = ('best', self.arguments['codec'])[self.arguments['codec'] is not None]
		self.videoquality = (None, self.arguments['video_quality'])[self.arguments['video_quality'] is not None]
		self.season = (False, True)[self.arguments["season_amazon"] is not False]
		self.episode = (None, self.arguments["episode"])[self.arguments["episode"] is not None]
		self.region = (universal().getConfig()['region'], self.arguments["region"])[
			self.arguments["region"] is not None]
		
		if self.region == 'pv':
			self.profile = (universal().getConfig()['prime_cookies'], self.arguments["profile"])[
			self.arguments["profile"] is not None] 
		if self.region == 'ca':
			self.profile = (universal().getConfig()['prime_cookies_ca'], self.arguments["profile"])[
			self.arguments["profile"] is not None] 			
		if self.region == 'us':
			self.profile = (universal().getConfig()['amazon_cookies_us'], self.arguments["profile"])[
			self.arguments["profile"] is not None]
		if self.region == 'uk':
			self.profile = (universal().getConfig()['amazon_cookies_uk'], self.arguments["profile"])[
			self.arguments["profile"] is not None]
		if self.region == 'de':
			self.profile = (universal().getConfig()['amazon_cookies_de'], self.arguments["profile"])[
			self.arguments["profile"] is not None]  
		if self.region == 'jp':
			self.profile = (universal().getConfig()['amazon_cookies_jp'], self.arguments["profile"])[
			self.arguments["profile"] is not None]	          

		if self.videoquality is not None:
			self.quality = self.videoquality

		"""this if statement sets the way the messages are display to the screen, this is a full"""
		"""debug logging"""
		if self.loglevel == logging.DEBUG:
			logging.basicConfig(
				format='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s',
				datefmt='%Y-%m-%d %I:%M:%S %p',
				level=self.loglevel,
			)
			logging.getLogger("requests").setLevel(logging.WARNING)

		"""basic logging that only shows the message"""
		if self.loglevel == logging.INFO:
			logging.basicConfig(
				format='%(message)s',
				level=self.loglevel,
			)
		
		self.logger = logging.getLogger(__name__)
		self.requestor = RequestHelper()
		self.params = AmazonParameters()

	def __asinHistory(self, asin):
		file = "pyamazon/items/{}.json".format(asin)
		if os.path.isfile(file):
			return True
		else:
			return False

	def _saveHistory(self, asin, data):
		if data is not None:
			file = "pyamazon/items/{}.json".format(asin)
			if not os.path.isdir("pyamazon/items/"):
				os.makedirs("pyamazon/items/")
			with open(file, "w") as writer:
				writer.write(json.dumps(data, indent=4))

	def SCRAP_ASINS(self, content):
		soup = Soup(content, 'html.parser')
		inputs = soup.findAll("li", {"class": "js-node-episode-container"})
		asins = []
		for li in inputs:
			if isinstance(li, Tag) and "av-ep-episodes" in str(li.get('id')):
				asin = li.find('input').get('id')
				asin = asin.replace("selector-", "")
				if asin not in asins:
					asins.append(asin)
		return asins

	def SearchASINPrimeVideo(self, asin):
		custom_headers_season = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'accept-encoding': 'gzip, deflate, br',
			'cache-control': 'no-cache',
			'accept-language': 'en-US,en;q=0.9,en;q=0.8',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
			'upgrade-insecure-requests': '1'}
		url = PRIME_BROWSE_URL.format(base_url="www.primevideo.com", asin=asin)
		html_data = requests.get(url, headers=custom_headers_season)
		html_data = html_data.text
		rg = re.compile(r'(<script type="text/template">)(.*)(</script>)')
		# rg = re.compile('(<script id="av-wconf-dv-web-player-cfg" type="application/json">)(.*)(</script><script type="text/javascript">P\\.when\\("av-widget-config"\\)\\.execute\\(function\\(widgetConfig\\){widgetConfig\\.declare\\("dv-web-player-cfg"\\);}\\);</script>)')
		rg2 = re.compile("(spty=')(.*)(')(.*)(pti=')")
		m = rg.search(html_data)
		m2 = rg2.search(html_data)
		conf_webplayer_json = json.loads(m.group(2))
		if m2:
			if m2.group(2) == 'Movie':
				amazonTypeTemp = 'movie'
			else:
				amazonTypeTemp = 'show'
			try:
				amazonTypeTemp = amazonTypeTemp
			except Exception:
				print('Error in URL.')
				sys.exit(0)

			if amazonTypeTemp == 'movie':
				asinMovie = conf_webplayer_json['pageTitleID']
				return (asinMovie, amazonTypeTemp)

			asinList = self.SCRAP_ASINS(html_data)
			return (asinList, amazonTypeTemp)

	def SearchASINAmazon(self, asin):
		custom_headers_season = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'accept-encoding': 'gzip, deflate, br',
			'cache-control': 'max-age=0',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
			'upgrade-insecure-requests': '1'}
		html_data = requests.get(asin, headers=custom_headers_season)
		data = html_data.text
		asin = re.search('<link rel="canonical" href="https://www.amazon.com.*/dp/(.+?)"', data)[1]
		return asin

	def runamazon(self):
		
		config = universal().getConfig()
		for key, value in config.items():
			if key in self.amazon_items and not value:
				raise ValueError('{} has no value, please set it in pyamazon/Configs/config.py.'.format(key))

		if self.season: 
			asins = self.asin.split(",")
			if self.asin == "None":				
				with open(self.file, "r") as reader:
					while True: 
						line = reader.readline()
						if not line:
							break
						asins.append(line.replace("\n", ""))

			for asin in asins:
				asinlist =[]
				if AMZONREGIONS[self.region]["primevideo"]:
					browse_response, type = self.SearchASINPrimeVideo(asin)
					for i, titleId in enumerate(browse_response):
						asinlist.append({"episode_number": i+1, 'asin': titleId})
				else:
					browse_response = self.requestor.getItems(
						url=AMZN_BROWSE_URL.format(base_url=AMZONREGIONS[self.region]["url"]),
						headers={
							"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
							"Accept-Encoding": "gzip, deflate, br",
							"Accept-Language": "en-US,en;q=0.9",
							"Cache-Control": "no-cache",
							"Connection": "keep-alive",
							"Host": "atv-ps.amazon.com",
							"Pragma": "no-cache",
							"Upgrade-Insecure-Requests": "1",
							"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"},
						params=self.params.browseparams(self.SearchASINAmazon(asin) if 'amazon' in asin else asin, AMZONREGIONS[self.region]["marketplaceID"]))
					
					try:
						for titles in browse_response.json()["message"]["body"]["titles"]:
							if titles["number"] != 0:
								asinlist.append({"episode_number": titles['number'], 'asin': titles['titleId']})
					except:
						self.logger.info("Error getting episodes from asin: {}".format(asin))
						self.logger.info(browse_response.url)
						self.logger.info(asin)
						pass

				if self.episode:
					if self.episode.__contains__("-"):
						episode_range = self.episode.split("-")
						for asin in asinlist:
							if asin['episode_number'] >= int(episode_range[0]):
								if asin['episode_number'] <= int(episode_range[1]):
									self.singles(asin=asin['asin'])
					else:
						self.logger.debug(json.dumps(asinlist, indent=4))
						for asin in asinlist:
							if asin['episode_number'] >= int(self.episode):
								self.singles(asin=asin['asin'])
				else:
					for asin in asinlist:
						self.singles(asin=asin['asin'])
		
		else:
			if self.asin == "None":
				asins = []
				with open(self.file, "r") as reader:
					while True:
						line = reader.readline()

						if not line:
							break
						asins.append(line.replace("\n", ""))
				for asin in asins:
					self.singles(asin)
			else:
				self.singles(asin=self.SearchASINAmazon(self.asin) if 'amazon' in self.asin else self.asin)

	def singles(self, asin):
		quality_lenght = len(self.quality.split(","))
		for quality in self.quality.split(","):
			if not self.__asinHistory(asin=asin):
				download = downloader(self.arguments)
				self._saveHistory(
					asin=asin,
					data=download.amazonrun(
						asin=asin,
						quality=quality,
						length=quality_lenght))
			else:
				redownload = universal().getConfig()['redownload_ID']
				if redownload.lower() == "yes":
					download = downloader(self.arguments)
					download.amazonrun(
						asin=asin,
						quality=quality,
						length=quality_lenght)
				
				if redownload.lower() == "ask":
					rerip = input("re-download asin?: ")
					if rerip.lower() in ["yes", "y"]:
						download = downloader(self.arguments)
						download.amazonrun(
							asin=asin,
							quality=quality,
							length=quality_lenght)

				elif redownload.lower() == "no":
					self.logger.info("Asin: {} has been downloaded before".format(asin))
