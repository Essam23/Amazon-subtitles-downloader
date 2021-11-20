import json, logging, os, sys, base64, time, re, traceback, subprocess, xmltodict, titlecase, untangle, random
from unidecode import unidecode
import pyamazon.Configs.Amazon as config
import pyamazon.Configs.config as universal
from pyamazon.Helpers.requesthelper import RequestHelper
from pyamazon.Params import AmazonParameters
from pyamazon.Parser import AmazonParser
from pyamazon.Decrypt.Amazon import AmazonDecrypt
from pyamazon.Helpers.processhelper import ProcessHelper
from pyamazon.Helpers.namehelper import rename
from pyamazon.Helpers.utility import *
from pyamazon.Configs.config import Config
from pyamazon.Helpers.proxy.nordvpn import nordAPI
from pyamazon.Helpers.proxy.privatevpn import privatevpnAPI

class AmazonDownloader(object):
	def __init__(self, *kwargs):
		self.working_dir = os.path.dirname(sys.modules['__main__'].__file__)
		self.arguments = json.loads(json.dumps(kwargs))[0]
		self.logger = logging.getLogger(__name__)
		self.config = config
		self.asin = self.arguments["asin"]		
		self.requesthelper = RequestHelper()
		self.amazonparams = AmazonParameters()
		self.amazonparser = AmazonParser()
		self.processhelper = ProcessHelper()
		self.output = (None, self.arguments['output'])[self.arguments['output'] is not None]
		self.proxy = (False, self.arguments["proxy"])[self.arguments["proxy"] is not None]
		self.proxyip = (False, self.arguments["proxyip"])[self.arguments["proxyip"] is not None]
		self.proxycode = (False, self.arguments["proxycode"])[self.arguments["proxycode"] is not None]
		self.proxyport = (False, self.arguments["proxyport"])[self.arguments["proxyport"] is not None]
		self.proxytype = (False, self.arguments["proxytype"])[self.arguments["proxytype"] is not None]
		self.audioquality = ("best", self.arguments["audio_quality"])[self.arguments["audio_quality"] is not None]
		self.lang = ([], self.arguments["audio_language"])[self.arguments["audio_language"] is not None]
		self.sub_lang = ([], self.arguments["sub_language"])[self.arguments["sub_language"] is not None]
		self.sub_others = ([], self.arguments["sub_others"])[self.arguments["sub_others"] is not None]
		self.chapterslang = (False, self.arguments["chapterslang"])[self.arguments["chapterslang"] is not None]
		self.default_audio_mux = ([], self.arguments["default_audio_mux"])[self.arguments["default_audio_mux"] is not None]
		self.default_sub_mux = ([], self.arguments["default_sub_mux"])[self.arguments["default_sub_mux"] is not None]
		self.noAD = ([], self.arguments["noAD"])[self.arguments["noAD"] is not None]		
		self.forced = ([], self.arguments["forced"])[self.arguments["forced"] is not None]		
		self.simple_rename = (False, True)[self.arguments["simple_rename"] is not False]
		self.keys = (False, self.arguments["keys"])[self.arguments["keys"] is not False]
		self.keep = (False, self.arguments["keep"])[self.arguments["keep"] is not False]
		self.uhd = (False, self.arguments["hdr"])[self.arguments["hdr"] is not False]
		self.nochapters = (False, self.arguments["nochapters"])[self.arguments["nochapters"] is not False]		
		self.original = (False, self.arguments["original"])[self.arguments["original"] is not False]
		self.hevc = (False, self.arguments["hevc"])[self.arguments["hevc"] is not False]         
		self.hdr = (False, self.arguments["hdr1080"])[self.arguments["hdr1080"] is not False]         
		self.size = (False, self.arguments["size"])[self.arguments["size"] is not False]
		self.links = (False, True)[self.arguments["links"] is not False]
		self.subs = (False, self.arguments["subs"])[self.arguments["subs"] is not False]
		self.season_amazon = (False, self.arguments["season_amazon"])[self.arguments["season_amazon"] is not False]	
		self.nosubs = (False, self.arguments["nosubs"])[self.arguments["nosubs"] is not False]
		self.novideo = (False, self.arguments["novideo"])[self.arguments["novideo"] is not False]
		self.noaudio = (False, self.arguments["noaudio"])[self.arguments["noaudio"] is not False]
		self.cache = (True, False)[self.arguments["overwrite"] is not False]
		self.aria2c = Config().getConfig()["aria2c"]
		self.SubtitleEdit = Config().getConfig()["subtitledit"]
		self.codec = ("H265", universal.Config().getConfig()['codec'])[self.arguments["hevc"] is not True]
		self.group = (universal.Config().getConfig()['group'], self.arguments["group"])[self.arguments["group"] is not None]
		self.region = (universal.Config().getConfig()['region'], self.arguments["region"])[self.arguments["region"] is not None]	
		if self.region == 'pv':
			self.profile = (universal.Config().getConfig()['prime_cookies'], self.arguments["profile"])[
			self.arguments["profile"] is not None] 
		if self.region == 'ca':
			self.profile = (universal.Config().getConfig()['prime_cookies_ca'], self.arguments["profile"])[
			self.arguments["profile"] is not None] 			
		if self.region == 'us':
			self.profile = (universal.Config().getConfig()['amazon_cookies_us'], self.arguments["profile"])[
			self.arguments["profile"] is not None]
		if self.region == 'uk':
			self.profile = (universal.Config().getConfig()['amazon_cookies_uk'], self.arguments["profile"])[
			self.arguments["profile"] is not None]
		if self.region == 'de':
			self.profile = (universal.Config().getConfig()['amazon_cookies_de'], self.arguments["profile"])[
			self.arguments["profile"] is not None]  
		if self.region == 'jp':
			self.profile = (universal.Config().getConfig()['amazon_cookies_jp'], self.arguments["profile"])[
			self.arguments["profile"] is not None]	
		if self.region == 'in':
			self.profile = (universal.Config().getConfig()['prime_cookies_in'], self.arguments["profile"])[
			self.arguments["profile"] is not None]	

		if self.region == 'pv' or self.region == 'in' or self.region == 'ca':
			self.gasc = True
		else:
			self.gasc = False       

		self.browseurl = config.AMZN_BROWSE_URL.format(base_url=self.config.AMZONREGIONS[self.region]["url"])
		self.resourceurl = config.AMZN_PARAMS_URL.format(base_url=self.config.AMZONREGIONS[self.region]["url"])
		
		self.headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9",
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"Host": "atv-ps.amazon.com",
			"Pragma": "no-cache",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"}

		if self.proxycode or self.proxyip:
			print('\nProxy on')

			if self.proxy == '':
				print('no proxy input, exit.')
				sys.exit(1)

			if self.proxy == 'privatevpn':
				proxy = universal.Config().getConfig()['privatevpn']
				print('Proxy Status: Activated-PrivateVpn')
				if self.proxycode:
					if ':' in str(self.proxycode):
						pcode = str(self.proxycode).split(':')[0]
						pproxy = privatevpnAPI.privatevpn(code=pcode, silentmode=True)
					else:
						pcode = str(self.proxycode)
						pproxy = privatevpnAPI.privatevpn(code=pcode, silentmode=False)
				elif self.proxyip:
					pproxy = str(self.proxyip)
				
				proxy_and_port = pproxy + ':' + proxy['port']
				Mainproxy = 'http://' + proxy['email'] + ':' + proxy['pass'] + '@' + proxy_and_port
				self.logger.info(Mainproxy)
				os.environ['http_proxy'] = Mainproxy
				os.environ['HTTP_PROXY'] = Mainproxy
				os.environ['https_proxy'] = Mainproxy
				os.environ['HTTPS_PROXY'] = Mainproxy
				print(nordAPI.checkproxy())	                	

			if self.proxy == 'nordvpn':
				print('Proxy Status: Activated-NordVpn')
				proxy = universal.Config().getConfig()['nordvpn']
				if self.proxycode:
					pproxy = nordAPI.loadcountry(self.proxycode)
					print('Proxy: ' + pproxy)
				
				if self.proxyip:
					pproxy = str(self.proxyip)
					print('Proxy: ' + pproxy)
			
				proxy_and_port = pproxy + ':' + proxy['port']
				Mainproxy = 'http://' + proxy['email'] + ':' + proxy['pass'] + '@' + proxy_and_port
				self.logger.info(Mainproxy)
				os.environ['http_proxy'] = Mainproxy
				os.environ['HTTP_PROXY'] = Mainproxy
				os.environ['https_proxy'] = Mainproxy
				os.environ['HTTPS_PROXY'] = Mainproxy
				print(nordAPI.checkproxy())

			if self.proxy == 'torgurd':
				print('Proxy Status: Activated-TorgurdVpn')
				proxy = universal.Config().getConfig()['torgurd']
				if self.proxycode == 'us': pproxy = proxy['us_ip']
				if self.proxycode == 'uk': pproxy = proxy['uk_ip']
				proxy_and_port = pproxy + ':' + proxy['port']
				Mainproxy = 'https://' + proxy['email'] + ':' + proxy['pass'] + '@' + proxy_and_port
				self.logger.info(Mainproxy)
				os.environ['http_proxy'] = Mainproxy
				os.environ['HTTP_PROXY'] = Mainproxy
				os.environ['https_proxy'] = Mainproxy
				os.environ['HTTPS_PROXY'] = Mainproxy
				print(nordAPI.checkproxy())

			if self.proxy == 'freeproxy':
				print('Proxy Status: Activated-FREE')
				if str(self.proxytype) == 'socks5':
					Mainproxy = 'socks5h://' + str(self.proxyip) + ':' + str(self.proxyport)
				else:
					Mainproxy = str(self.proxytype) + '://' + str(self.proxyip) + ':' + str(self.proxyport)
				self.logger.info(Mainproxy)
				os.environ['http_proxy'] = Mainproxy
				os.environ['HTTP_PROXY'] = Mainproxy
				os.environ['https_proxy'] = Mainproxy
				os.environ['HTTPS_PROXY'] = Mainproxy
				print(nordAPI.checkproxy())

		else:
			print('\nProxy off')


	#####################################################################################################################################

	def setouput(self, file):
		total = 0
		configOutput = universal.Config().getConfig()['output']
		output = None
		if self.output is None:
			if configOutput is not None:
				output = os.path.join(configOutput, file)
				if not os.path.exists(configOutput):
					os.makedirs(configOutput)
			else:
				output = os.path.join(self.working_dir, "output")
				if not os.path.exists(output):
					os.makedirs(output)
				output = os.path.join(output, file)
		else:
			if not os.path.exists(self.output):
				os.makedirs(self.output)
			output = os.path.join(self.output, file)
		if not output:
			raise ValueError('you failed to set an output folder, whether its via command or via config')
		total = total + 1
		if total == 1:
			self.logger.debug("Output Folder: {}".format(output))
		return output

	#####################################################################################################################################

	def ReplaceChaptersNumber(self,X):
		pattern1 = re.compile('(\\d+)(\\.)( )')
		X = pattern1.sub('', X)
		return X	


	def ReplaceDontLikeWord(self, X):
		return X.replace(' : ', ' - ').replace(': ', ' - ').replace(':', ' - ').replace('&', 'and').replace('+', '').replace(';', '').replace('ÃƒÂ³', 'o').replace('[', '').replace("'", '').replace(']', '').replace('/', '').replace('//', '').replace('’', "'").replace('*', 'x').replace('<', '').replace("4K UHD ", "").replace('.-.', '-').replace('>', '').replace('|', '').replace('~', '').replace('#', '').replace('%', '').replace('{', '').replace('}', '').replace(',', '').replace('?', '').encode('latin-1').decode('latin-1')	

	def ReplaceCodeLanguagesforsubs(self, X):
		##https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
		return X.replace('las', 'es').replace('cmn', 'zh').replace('Deutsch', 'German').replace('Español (España)', 'Castilian').replace('Español (Latinoamérica)', 'Spanish').replace('Español', 'Spanish').replace('Français', 'French').replace('Indonesia', 'Indonesian').replace('Italiano', 'Italian').replace('Nederlands', 'Dutch').replace('Polski', 'Polish').replace('Português', 'Portuguese').replace('Türkçe', 'Turkish').replace('Русский', 'Russian').replace('العربية', 'Arabic').replace('हिन्दी', 'Hindi').replace('中文（简体）', 'Chinese (Simplified)').replace('中文（繁體）', 'Chinese (Traditional)').replace('中文', 'Chinese').replace('한국어', 'Korean').replace('日本語', 'Japanese').replace('Dansk', 'Danish').replace('Norsk Bokmål', 'Norwegian').replace('Norsk', 'Norwegian').replace('Suomi', 'Finnish').replace('Svenska', 'Swedish').replace('தமிழ்', 'Tamil').replace('తెలుగు', 'Telugu').replace('עברית', 'Hebrew').replace('ไทย', 'Thai').replace('Català', 'Catalan').replace('मराठी', 'Marathi').replace('বাংলা', 'Bangla').replace('Shqip', 'Albanian').replace('Čeština', 'Czech').replace('Български', 'Bulgarian').replace('ישראל', 'Israel').replace('Ελληνικά', 'Greek').replace('Hrvatski', 'Croatian').replace('Magyar', 'Hungarian').replace('Română', 'Romanian').replace('Slovenščina', 'Slovenian').replace('Македонски', 'Macedonian').replace('Српски', 'Serbian').replace('Bosanski', 'Bosnian').replace('Bahasa Melayu', 'Malay').replace('اردو', 'Urdu').replace('فارسی', 'Persian').replace('Tl', 'Tagalog').replace('ລາວ', 'Lao').replace('አማርኛ', 'Amharic').replace('Հայերեն', 'Armenian').replace('Euskara', 'Basque').replace('ქართული', 'Georgian').replace('ગુજરાતી', 'Gujarati').replace('Íslenska', 'Icelandic').replace('ಕನ್ನಡ', 'Kannada').replace('Қазақ Тілі', 'Kazakh').replace('Ikinyarwanda', 'Kinyarwanda').replace('Кыргызча', 'Kirghiz').replace('latviešu', 'Latvian').replace('Lietuvių', 'Lithuanian').replace('മലയാളം', 'Malayalam').replace('Монгол', 'Mongolian').replace('नेपाली', 'Nepali').replace('ਪੰਜਾਬੀ', 'Punjabi').replace('Kiswahili', 'Swahili').replace('བོད་སྐད་', 'Tibetan').replace('Українська', 'Ukrainian').replace('Tiếng Việt', 'Vietnamese').replace('پښتو', 'Afghani').replace('Eesti', 'Estonian')

	#####################################################################################################################################

	def get_resources(self, asin, codec):		
		api_keys = self.get_init_info(asin, codec)
		if not api_keys :
			self.logger.warning("Please verify asin, cookies, and vpn if valid and try again")
			exit(-1)
		if api_keys is not False:
			self.subsList = []
			if self.forced:
				if api_keys['debug']['forcedNarratives']:
					for subtitle in api_keys['debug']['forcedNarratives']:
						url = str(subtitle['url']).replace('.dfxp', '.srt')
						lang = str(subtitle["languageCode"]).split("-")[0]
						if len(self.forced) == 0 or (len(self.forced) > 0 and lang in self.forced):
							name = subtitle["displayName"]							
							if not self.nosubs:
								self.subsList.append({
									"url": url,
									"name": self.ReplaceCodeLanguagesforsubs(name),
									'lang': self.ReplaceCodeLanguagesforsubs(lang),
									'forced': True,
									'track': subtitle.get('type')})

			if self.original:
				if api_keys['debug']['forcedNarratives']:
					for subtitle in api_keys['debug']['forcedNarratives']:
						if (subtitle['timedTextTrackId'].replace('_narrative', '')) == api_keys['debug']["audioVideoUrls"]['defaultAudioTrackId']:
							url = str(subtitle['url']).replace('.dfxp', '.srt')
							name = str(subtitle["displayName"])
							if not self.nosubs:
								self.subsList.append({
									"url": url,
									"name": self.ReplaceCodeLanguagesforsubs(name),
									'forced': True,
									'track': subtitle.get('type')})
							
			
			if api_keys['debug']['subtitleUrls']:
				for subtitle in api_keys['debug']['subtitleUrls']:
					url = str(subtitle['url']).replace('.dfxp', '.srt')
					lang = str(subtitle["languageCode"]).split("-")[0]
					if len(self.sub_lang) == 0 or (len(self.sub_lang) > 0 and lang in self.sub_lang):
						name = subtitle["displayName"]
						if not self.nosubs:
							self.subsList.append({
								"url": url,
								"name": self.ReplaceCodeLanguagesforsubs(name),
								'lang': self.ReplaceCodeLanguagesforsubs(lang),
								'forced': False,
								'track': subtitle.get('type')})
							self.logger.debug('Subtitle URL: {}'.format(url))
							self.logger.debug('Subtitle Lang: {}'.format(lang))
			
			else:
				self.isSubs = False
			
			return api_keys

	#####################################################################################################################################

	def get_vbr_streams(self, asin, codec):
		url = self.config.AMZN_VIDEO_INFO_URL.format(
			base_url=self.config.AMZONREGIONS[self.region]["url"],
			asin=asin,
			device_id=self.config.AMAZON_DEVICE_ID,
			device_type_id=self.config.AMAZON_DEVICE_TYPE_ID,
			marketplace_id=self.config.AMZONREGIONS[self.region]["marketplaceID"],
			customer_id=self.config.AMZONREGIONS[self.region]['customerId'],
			token=self.config.AMZONREGIONS[self.region]['token'],
			profile="H265" if self.uhd or self.hevc or self.hdr else "H264",
			bitrate="CVBR%2CCBR",
			hevc='deviceVideoCodecOverride=H265' if self.hevc else '',
			gasc=self.gasc,
			uhd="&deviceVideoQualityOverride=UHD&deviceVideoCodecOverride=H265&deviceHdrFormatsOverride=Hdr10" if self.uhd or self.hdr else ""
		)
		headers = self.config.AMAZON_VIDEO_INFO_HEADERS
		headers['Origin'] = "https://{0}".format(self.config.AMZONREGIONS[self.region]["url"])
		resources_req = self.requesthelper.getItems(url=url, headers=headers, user=self.profile)
		if not resources_req:
			return False, False
		try:
		
			resources_json = json.loads(resources_req.text)
			av_urls_json = resources_json['audioVideoUrls']['avCdnUrlSets']
		except Exception:
			self.logger.error("No rights/incorrect region")
			return False, False
			sys.exit(0)
		return resources_json, av_urls_json

	#####################################################################################################################################

	def get_cbr_streams(self, asin, codec):
		url = self.config.AMZN_VIDEO_INFO_URL.format(
			base_url=self.config.AMZONREGIONS[self.region]["url"],
			asin=asin,
			device_id=self.config.AMAZON_DEVICE_ID,
			device_type_id=self.config.AMAZON_DEVICE_TYPE_ID,
			marketplace_id=self.config.AMZONREGIONS[self.region]["marketplaceID"],
			customer_id=self.config.AMZONREGIONS[self.region]['customerId'],
			token=self.config.AMZONREGIONS[self.region]['token'],
			profile="H264",
			bitrate="CBR",
			hevc='',
			gasc=self.gasc,
			uhd=""
		)
		headers = self.config.AMAZON_VIDEO_INFO_HEADERS
		headers['Origin'] = "https://{0}".format(self.config.AMZONREGIONS[self.region]["url"])
		resources_req = self.requesthelper.getItems(url=url, headers=headers, user=self.profile)
		try:
			resources_json = json.loads(resources_req.text)
			av_urls_json = resources_json['audioVideoUrls']['avCdnUrlSets']
		except:
			self.logger.error("No rights/incorrect region")
			sys.exit(0)

		return av_urls_json

	#####################################################################################################################################	

	def get_audio_streams(self, asin, codec):
		url = self.config.AMZN_VIDEO_INFO_URL.format(       
			base_url=self.config.AMZONREGIONS[self.region]["url"],      
			asin=asin,      
			device_id=self.config.AMAZON_DEVICE_ID,     
			device_type_id=self.config.AMAZON_DEVICE_TYPE_ID,       
			marketplace_id=self.config.AMZONREGIONS[self.region]["marketplaceID"],      
			customer_id=self.config.AMZONREGIONS[self.region]['customerId'],        
			token=self.config.AMZONREGIONS[self.region]['token'],       
			profile="H264",     
			bitrate="CVBR%2CCBR",  
			hevc='',     
			gasc=self.gasc,     
			uhd=""      
		)       
		headers = self.config.AMAZON_VIDEO_INFO_HEADERS     
		headers['Origin'] = "https://{0}".format(self.config.AMZONREGIONS[self.region]["url"])      
		resources_req = self.requesthelper.getItems(url=url, headers=headers, user=self.profile)       
		try:        
			resources_json = json.loads(resources_req.text)     
			av_urls_json = resources_json['audioVideoUrls']['avCdnUrlSets']     
		except KeyError:        
			self.logger.error("No rights/incorrect region")        
			#return False
			sys.exit(0)     
		return av_urls_json 

	#####################################################################################################################################    

	def get_init_info(self, asin, codec):
		
		resources_json, vbr_streams = self.get_vbr_streams(asin, codec)
		if not vbr_streams:
			return False

		if not self.subs:
			if not self.uhd:
				if not self.hdr:
					if not self.hevc:
						cbr_streams = self.get_cbr_streams(asin, codec)
						if not cbr_streams:
							return False
			
			audio_streams = self.get_audio_streams(asin, codec)     
			if not audio_streams:       
				return False
				
			cert_base64 = self.get_cert_info(asin)
			if cert_base64 is None:
				return False

			videoCDNS = []
			
			cdnsVideoVBRparser = self.amazonparser.cdns(vbr_streams)
			videoCDNS.append(random.choice([
				{"cdn": x['cdn'], "url": x['avUrlInfoList'][0]['url'], "weight": x['cdnWeightsRank'], "type": "video", "profile":"VBR"}
				for x in cdnsVideoVBRparser]))
			
			if not self.uhd:
				if not self.hdr:
					if not self.hevc: 
						cdnsVideoCBRparser = self.amazonparser.cdns(cbr_streams)
						videoCDNS.append(random.choice([
							{"cdn": x['cdn'], "url": x['avUrlInfoList'][0]['url'], "weight": x['cdnWeightsRank'], "type": "video", "profile":"CBR"}
							for x in cdnsVideoCBRparser]))

			cdnsAudioParser = self.amazonparser.cdns(audio_streams)
			cdnsAudio = random.choice([{"cdn": x['cdn'], "url": x['avUrlInfoList'][0]['url'], "weight": x['cdnWeightsRank'], "type": "audio"} for x in cdnsAudioParser])

			
			keys = []
			amazon_decrypt = AmazonDecrypt(asin, self.region, self.profile)
			
			self.logger.info('\nGetting Audio...')
			mpd_audio = self.get_mpd(cdnsAudio)
			if mpd_audio is None:
				self.logger.debug("Audio mpd not found")
				return False
			
			init_data_b64 = self.get_data_b64(mpd_audio)
			if init_data_b64 is None:
				self.logger.debug("pssh not found")
				return False

			key = amazon_decrypt.do_decrypt({"init_data_b64": init_data_b64, "cert_data_b64": cert_base64})
			if not key:
				self.logger.info("Audio keys not found")
				exit(1)
			if self.keys:
				keys.append('Audio KEYS:')
			keys.extend(key)
			
			mpd_video = []
			for selected_cdn in videoCDNS:
				if self.uhd: 
					self.logger.info('Getting UHD HDR...')
				elif self.hdr:
					self.logger.info('Getting HDR...')					
				elif self.hevc:
					self.logger.info('Getting HEVC...')
				else:
					self.logger.info('Getting {}...'.format(selected_cdn['profile']))	
				get_mpd_video = self.get_mpd(selected_cdn)
				if get_mpd_video is None:
					self.logger.debug("mpd not found")
					return False
				init_data_b64 = self.get_data_b64(get_mpd_video)
				if init_data_b64 is None:
					self.logger.debug("init_data_b64 not found")
					return False
				if self.keys:
					if self.uhd: keys.append('UHD HDR KEYS:')
					elif self.hdr: keys.append('HDR KEYS:')
					elif self.hevc: keys.append('HEVC KEYS:')
					else:			
						keys.append('{} KEYS:'.format(selected_cdn['profile']))
				keys.extend(amazon_decrypt.do_decrypt({"init_data_b64": init_data_b64, "cert_data_b64": cert_base64}))
				mpd_video.append({'url': selected_cdn, 'data': get_mpd_video})
		
		if self.subs:
			return {"debug": resources_json}
			
		return {"debug": resources_json, "keys": keys, "cdns_video": videoCDNS, "cdns_audio": [cdnsAudio],
				"mpd_video": mpd_video, "mpd_audio": mpd_audio}

	#####################################################################################################################################

	def get_mpd(self, selected_cdn):
		self.logger.debug("original mpd url: {}".format(selected_cdn['url']))
		m = re.match(r'(https?:\/\/.*\/)d.{0,1}\/.*~\/(.*)', selected_cdn['url'])
		mpd_url = m.group(1) + m.group(2)
		self.logger.debug("selected CDN {} with MPD url {}".format(selected_cdn['cdn'], mpd_url))
		self.logger.debug("requesting mpd xml at URL {}".format(mpd_url))

		mpd_dict = None
		try:
			mpd_req = self.requesthelper.getItems(url=mpd_url, user=self.profile)
			if mpd_req:
				mpd_dict = xmltodict.parse(mpd_req.text)
		except Exception as e:
			self.logger.debug(e)
			self.logger.debug("Mpd dowload failed.")
			return mpd_dict

		return mpd_dict

	#####################################################################################################################################

	def get_cert_info(self, asin):
		cert_base64 = None
		cert_request = b'\x08\x04'
		amazon_decrypt = AmazonDecrypt(asin, self.region, self.profile)
		return amazon_decrypt.get_license(cert_request)

	#####################################################################################################################################

	def get_data_b64(self, mpd_dict):
		for content in mpd_dict['MPD']['Period']['AdaptationSet']:
			if content['@group'] == '2':
				for videocontent in content['ContentProtection']:
					if videocontent['@schemeIdUri'] == self.config.WIDEVINE_PSSH_URN:
						videopssh = videocontent['cenc:pssh']
						break
		if videopssh:
			init_data_b64 = videopssh
			self.logger.debug("init_data found in mpd")
			self.logger.debug("init_data - {}".format(init_data_b64))
			return init_data_b64
		else:
			self.logger.error("init data not found in mpd, exiting")
			return None

	######################################################################################################################################
		
	def audiolang(self, data, language_list):
		
		langs = []

		try:
			for lang in language_list:
				for languages in data["catalogMetadata"]["playback"]["audioTracks"]:
					lang_name = self.ReplaceCodeLanguagesforsubs(languages["displayName"])
					if str(lang_name).lower() == str(lang).lower() or \
					 str((languages["language"]).split('_')[0]).lower() == str(lang).lower():
						if self.noAD:					    	
							if not languages['type'] == 'descriptive':
								langs.append({'language': lang_name, 'lang': str(languages["id"])}) 
						else:
							langs.append({'language': lang_name, 'lang': str(languages["id"])})
		
		except KeyError:
			for lang in language_list:
				for languages in data["catalogMetadata"]["playback"]["audioTracks"]:
					lang_name = self.ReplaceCodeLanguagesforsubs(languages["displayName"])
					if str(lang_name).lower() == str(lang).lower() or \
					 str((languages["language"]).split('_')[0]).lower() == str(lang).lower():
						if self.noAD:					    	
							if not languages['type'] == 'descriptive':
								langs.append({'language': lang_name, 'lang': str((languages["language"]).split('_')[0])})
						else:
							langs.append({'language': lang_name, 'lang': str((languages["language"]).split('_')[0])})

		except KeyError:
			for lang in language_list:
				for languages in data['audioVideoUrls']["audioTrackMetadata"]:
					lang_name = self.ReplaceCodeLanguagesforsubs(languages["displayName"])
					if str(lang_name).lower() == str(lang).lower() or \
					 ("language" in languages and str((languages["language"]).split('_')[0]).lower() == str(lang).lower()) \
					  or ("languageCode" in languages and str(lang).lower() in str(languages['languageCode']).lower()):
						if self.noAD:					    	
							if not lang['audioSubtype'] == 'descriptive':
								langs.append({'language': lang_name,'lang': str(languages["audioTrackId"])})
						else:
							langs.append({'language': lang_name,'lang': str(languages["audioTrackId"])})


		except KeyError:
			for lang in language_list:
				for languages in data['audioVideoUrls']["audioTrackMetadata"]:
					lang_name = self.ReplaceCodeLanguagesforsubs(languages["displayName"])
					if str(lang_name).lower() == str(lang).lower() or \
					 ("language" in languages and str((languages["language"]).split('_')[0]).lower() == str(lang).lower()) \
					  or ("languageCode" in languages and str(lang).lower() in str(languages['languageCode']).lower()):
						if self.noAD:					    	
							if not lang['audioSubtype'] == 'descriptive':
								langs.append({'language': lang_name, 'lang': str((lang['languageCode']).split('-')[0])})
						else:
							langs.append({'language': lang_name, 'lang': str((lang['languageCode']).split('-')[0])})


		if len(langs) == 0:
			if self.original:
				try:
					for lang in data["audioVideoUrls"]["audioTrackMetadata"]:
						if lang['audioTrackId'] == data["audioVideoUrls"]['defaultAudioTrackId']:
							langs.append({'language': lang['displayName'], 'lang': str(lang['audioTrackId'])}) 

				except KeyError:
					for lang in data["audioVideoUrls"]["audioTrackMetadata"]:
						#if not lang['audioSubtype'] == 'descriptive':
							langs.append({'language': lang['displayName'], 'lang': str(lang['audioTrackId'])})   

			else:
				try:
					for lang in data["audioVideoUrls"]["audioTrackMetadata"]:
						#if not lang['audioSubtype'] == 'descriptive':
							langs.append({'language': lang['displayName'], 'lang': str(lang['audioTrackId'])})

				except KeyError:            
					for lang in data["audioVideoUrls"]["audioTrackMetadata"]:
						#if not lang['audioSubtype'] == 'descriptive':
							langs.append({'language': lang['displayName'], 'lang': str((lang['languageCode']).split('-')[0])})				
				
				except KeyError:
					for languages in data["catalogMetadata"]["playback"]["audioTracks"]:
						#if not languages['type'] == 'descriptive':
							langs.append({'language': languages["displayName"], 'lang': str(languages["id"])})				

				except KeyError:
					for languages in data["catalogMetadata"]["playback"]["audioTracks"]:
						#if not languages['type'] == 'descriptive':
							langs.append({'language': languages["displayName"], 'lang': str((languages["language"]).split('_')[0])})				
		return langs

	######################################################################################################################################	

	def amazonrun(self, asin, quality, length):
		
		metadata = self.get_resources(asin=asin, codec=self.codec)
		if metadata:
			return self.amazonprocessor(data=metadata, quality=quality, length=length)
		if not metadata:
			pass

	def amazonprocessor(self, data, quality, length):
		
		if self.chapterslang: chapterslang = self.chapterslang
		else: chapterslang = 'en-US'

		output = os.path.join(self.working_dir, "output\\")
		content_type = data['debug']['catalogMetadata']['catalog']['type']
		xray_params = self.amazonparams.vcid_params(vcid=data['debug']['returnedTitleRendition']['contentId'], region=self.region, chapterslang=chapterslang)
		xray_response = self.requesthelper.getItems(url=xray_params['url'], params=xray_params['params'], user=self.profile)
		xray_name = self.amazonparser.name(xray_response=xray_response, type=content_type, data=data, skipxray=self.simple_rename)
		if xray_response:
			chapters = self.amazonparser.chapters(xray_response=xray_response.json(), type=content_type, data=data)
		else:
			chapters = []		
		try:
			if "EPISODE" in str(content_type):
				if not xray_name:
					self.logger.warning("something went wrong when grabbing the name, please report it back to me!")
					exit(-1)
				name = xray_name

			elif str(content_type) == "MOVIE":
				name = xray_name
		except Exception as err:
			self.logger.warning(err)
			name = xray_name
		name = unidecode(name)
		name = self.ReplaceDontLikeWord(name_checker(name))
		
		self.logger.info("\nRipping: {}".format(name))

		if self.subs:
			
			self.logger.info("\nSubtitles: ")
			for subtitles in self.subsList:
				if not subtitles['track'] == 'narrative':
					x = subtitles['name']
					print(x, end=' ' '\n')
					self.processhelper.legacyDownloader(url=subtitles["url"], name="{} {} {}.srt".format(
							self.setouput(name), subtitles['name'], subtitles['track']))
			
			ara = self.setouput('{} Arabic subtitle.srt'.format(name))
			if os.path.isfile(ara):       
				subprocess.call([self.SubtitleEdit, "/convert", ara, "srt", "/reversertlstartend", "/overwrite"], stdout=(open(os.devnull, 'wb')))							
			
		else:            
			videourls = self.amazonparser.mpds(data=data['mpd_video'], type="video")
			video_data = self.amazonparser.getvideo(manifest=videourls, videoquality=quality, display=self.links, hdr=self.hdr)
			video_url = self.amazonparser.spliturls(base=[video_data['manifest']], extension=video_data)

			if self.size:
				size = self.amazonparser.getvideo_size(video_url[0])
				self.logger.info("{}".format(size))
				return			

			audio_lang = self.audiolang(data['debug'], self.lang)					
			for alang in audio_lang:				
				lang_audio = self.ReplaceCodeLanguagesforsubs(alang['lang'])
				name_audio_lang = self.ReplaceCodeLanguagesforsubs(alang['language'])				
			
			for lang in audio_lang:
				if len(audio_lang) >= 2:
				   multiaudio = True
				else:
					multiaudio = False				

			audiourls = self.amazonparser.mpds(data=data['mpd_audio'], type="audio")
			audios_data = self.amazonparser.getaudio(manifest=audiourls, language=audio_lang, aac=False, audioquality=self.audioquality, display=self.links)
			audio_urls = []
			for audio_data in audios_data:
				audio_url = self.amazonparser.spliturls(base=data['cdns_audio'], extension=audio_data)
				audio_urls.append({'language': audio_data['lang'], 'urls': audio_url})		
			audio_encrypted = audiourls['audioencrypted']
			self.logger.debug("Audio not encrypted: {}".format(audio_encrypted))

			if self.links:
				return

			keys_file = 'KEYS_AMAZON_PRIMEVIDEO.txt'
			with open(keys_file, 'a+', encoding='utf8') as (file):
				if self.hevc: file.write('{}'.format(('\n'+ name +' [HEVC]' +'\n')))
				elif self.uhd: file.write('{}'.format(('\n'+ name +' [UHD 4K]' +'\n'))) 
				elif self.hdr: file.write('{}'.format(('\n'+ name +' [HDR]' +'\n'))) 				
				else: file.write('{}'.format(('\n'+ name +'\n'))) 
			
			if self.hevc: print("\n==HEVC KEYS==")
			elif self.uhd: print("\n==UHD KEYS==")
			elif self.hdr: print("\n==HDR KEYS==")
			else: print('\n==KEYS==')
			
			for key in data['keys']:
				self.logger.info(key)
				with open(keys_file, 'a+', encoding='utf8') as (file):
					file.write(key+'\n')
			
			if self.keys:
				return
									
			self.logger.info("\nQuality: {}".format(quality))			

			self.logger.info('\nAudio:')		
			for alang in audio_lang:
				lang_audio = self.ReplaceCodeLanguagesforsubs(alang['lang'])
				name_audio_lang = self.ReplaceCodeLanguagesforsubs(alang['language'])
				print(name_audio_lang, '[original]' if self.original else '', end=' ' '\n')

			self.logger.info("\nSubtitles: ")
			for subtitles in self.subsList:				
				if not subtitles['track'] == 'narrative':
					x = subtitles['name']
					print(x, end=' ' '\n')
					sub = "{} {} {}.srt".format(self.setouput(name), subtitles['name'], subtitles['track'])
					if not os.path.isfile(sub):
						self.processhelper.legacyDownloader(url=subtitles["url"], name="{} {} {}.srt".format(
								self.setouput(name), subtitles['name'], subtitles['track']))
			
			ara = self.setouput('{} Arabic subtitle.srt'.format(name))
			if os.path.isfile(ara):       
				subprocess.call([self.SubtitleEdit, "/convert", ara, "srt", "/reversertlstartend", "/overwrite"], stdout=(open(os.devnull, 'wb')))						

			if self.forced or self.original:
				self.logger.info("\nForced Subtitles: ")
				for subtitles in self.subsList:
					if subtitles['track'] == 'narrative':
						x = subtitles['name']
						print(x, end=' ' '\n')
						sub = "{} {} {}.srt".format(self.setouput(name), subtitles['name'], subtitles['track'])
						if not os.path.isfile(sub):
							self.processhelper.legacyDownloader(url=subtitles["url"], name="{} {} {}.srt".format(
							self.setouput(name), subtitles['name'], subtitles['track']))

			if not self.nochapters:
				if len(chapters) > 0:
					if os.path.isfile(self.setouput("{} Chapters.txt".format(name))):
						self.logger.info("\nChapters has already been successfully downloaded previously.")
					else:
						count = 1
						try:
							with open(self.setouput("{} Chapters.txt".format(name)), 'a', encoding='utf-8') as (f):
								for k, v in chapters.items():
									if int(count) >= 10:
										ChapterNumber = str(count)
									else:
										ChapterNumber = '0' + str(count)
									ChapterName = str(k).replace("['", '').replace("']", '').replace('’', "'")
									ChapterTime = str(v).replace("['", '').replace("']", '') + '.000'
									f.write(
										'CHAPTER' + ChapterNumber + '=' + ChapterTime + '\n' + 'CHAPTER' + ChapterNumber + 'NAME=' + self.ReplaceChaptersNumber(
											ChapterName).encode('latin-1').decode('latin-1') + '\n')
									count = count + 1

							self.logger.info('\nDone Writing Chapters!')
						except Exception:
							os.remove(self.setouput("{} Chapters.txt".format(name)))
				else:
					self.logger.info('\nNo chapters available.')												

			if not self.novideo:
				fmt_video_name_d = f'{output}{name} Decrypted Video [{quality}].mp4'
				fmt_video_name = f'{output}{name} Encrypted Video [{quality}].mp4'
				fmt_video_name_c = f'{output}{name} Encrypted Video [{quality}].mp4.aria2'
				if not os.path.isfile(fmt_video_name_d):
					if os.path.isfile(fmt_video_name_c):	
						self.logger.info("\nDownloading video...")
						self.processhelper.downloader(urls=video_url, output=self.setouput("{} Encrypted Video [{}].mp4".format(name, quality)))
					elif not os.path.isfile(fmt_video_name):	
						self.logger.info("\nDownloading video")
						self.processhelper.downloader(urls=video_url, output=self.setouput("{} Encrypted Video [{}].mp4".format(name, quality)))
					else:
						self.logger.info('\nVideo was previously downloaded')

					if not os.path.isfile(fmt_video_name.replace("Encrypted", "Decrypted")):    
						self.logger.info("\nDecrypting video")
						self.processhelper.decrypt(
							encrypted=self.setouput("{} Encrypted Video [{}].mp4".format(name, quality)),
							decrypted=self.setouput("{} Decrypted Video [{}].mp4".format(name, quality)),
							keys=data)
						os.remove(f'{output}{name} Encrypted Video [{quality}].mp4')
					else:
						pass
			
			if not self.noaudio:
				
				for audio_url in audio_urls:
					fmt_audio_name = "{} {} Audio{}.mp4".format(name, audio_url['language'] if multiaudio is True else lang_audio, " Encrypted" if not audio_encrypted else "")
					if not os.path.isfile(self.setouput(fmt_audio_name.replace("Encrypted", "Decrypted"))):
						self.logger.info("\nDownloading audio")
						self.processhelper.downloader(urls=audio_url['urls'], output=self.setouput(fmt_audio_name))
						if audio_encrypted is False:
							self.logger.info("\nDecrypting audio")
							self.processhelper.decrypt(
								encrypted=self.setouput(fmt_audio_name),
								decrypted=self.setouput(fmt_audio_name.replace("Encrypted", "Decrypted")),
								keys=data)
					else:
						self.logger.info("\nAudio was previously downloaded")        

			if self.novideo or self.noaudio:
				pass
				self.logger.info("Cleaning directory...")
				for files in os.listdir(os.path.dirname(self.setouput(name))):
					if name in files:
						f = self.setouput(files)
						if audio_encrypted is False:
							if not f.endswith("Decrypted.mp4"):
								if not f.endswith('.srt'):
									os.remove(f)	
				if not self.season_amazon:		
					sys.exit(0)

			else:
				if not os.path.isfile("{}.mkv".format(self.setouput(name))):					
					self.logger.info("\nMuxing")	
					mkvmerge_command = ['-o', "{}.mkv".format(self.setouput(name))]
					mkvmerge_command.append(f'{output}{name} Decrypted Video [{quality}].mp4')
					mkvmerge_command.append('--language')
					mkvmerge_command.append("0:und")

					muxer_defaults = {'audio':None, 'sub':None}
					if self.default_audio_mux: muxer_defaults.update({'audio': str(self.default_audio_mux)})
					else: muxer_defaults.update({'audio': 'en'})
					if self.default_sub_mux: muxer_defaults.update({'sub': str(self.default_sub_mux)})
					else: muxer_defaults.update({'sub': 'en'})

					for alang in audio_lang:
						l = (alang['lang']).split('-')[0]
						if '_' in l:
							l = l.split('_')[0] 
						lang_audio = self.ReplaceCodeLanguagesforsubs(l)
						lang = self.ReplaceCodeLanguagesforsubs(alang["language"])				
						fmt_audio_name = "{} {} Audio{}.mp4".format(name, alang['lang'], " Encrypted" if not audio_encrypted else "")
						mkvmerge_command.append('--language')
						mkvmerge_command.append("0:{}".format(lang_audio))
						if self.default_audio_mux:
							if muxer_defaults['audio'] == str(lang_audio):
								if not 'descriptive' in fmt_audio_name:						
									mkvmerge_command.append('--default-track')
									mkvmerge_command.append('0:yes')
						else:							
							mkvmerge_command.append('--default-track')
							mkvmerge_command.append('0:no')				
						mkvmerge_command.append('--track-name')
						mkvmerge_command.append('0:{}'.format(lang))
						mkvmerge_command.append(self.setouput(fmt_audio_name.replace("Encrypted", "Decrypted")))

					for subtitles in self.subsList:
						if os.path.exists("{} {} {}.srt".format(self.setouput(name), subtitles['name'], subtitles['track'])):
							mkvmerge_command.append('--sub-charset')
							mkvmerge_command.append('0:UTF-8')
							mkvmerge_command.append('--language')
							mkvmerge_command.append('0:{}'.format(subtitles["lang"]))
							if self.default_sub_mux:
								if muxer_defaults['sub'] == str(subtitles["lang"]):
									if not subtitles['track'] == 'narrative':
										mkvmerge_command.append('--forced-track')
										mkvmerge_command.append('0:no')							
										mkvmerge_command.append('--default-track')
										mkvmerge_command.append('0:yes')
							else:							
								mkvmerge_command.append('--default-track')
								mkvmerge_command.append('0:no')
							mkvmerge_command.append('--track-name')
							if subtitles['track'] == 'narrative':
								mkvmerge_command.append('0:{}{}'.format(subtitles["name"].replace('forced narrative', ''), "[Forced]"))
								mkvmerge_command.append('--forced-track')
								mkvmerge_command.append('0:yes')
							else:
								mkvmerge_command.append('0:{}{}'.format(subtitles["name"], "[SDH]" if subtitles['track'] == "sdh" else ""))
							mkvmerge_command.append("{} {} {}.srt".format(self.setouput(name), subtitles['name'], subtitles['track']))

					if self.sub_others:
						if os.path.exists("{} {} {}.srt".format(self.setouput(name), 'Polish', 'subtitle')):
							mkvmerge_command.append('--sub-charset')
							mkvmerge_command.append('0:UTF-8')
							mkvmerge_command.append('--language')
							mkvmerge_command.append('0:{}'.format('pl'))
							if self.default_sub_mux:
								if muxer_defaults['sub'] == 'pl':
									mkvmerge_command.append('--forced-track')
									mkvmerge_command.append('0:no')							
									mkvmerge_command.append('--default-track')
									mkvmerge_command.append('0:yes')
							else:							
								mkvmerge_command.append('--default-track')
								mkvmerge_command.append('0:no')
							mkvmerge_command.append('--track-name')
							mkvmerge_command.append('0:{}'.format('Polish'))
							mkvmerge_command.append("{} {} {}.srt".format(self.setouput(name), 'polish', 'subtitle'))

					if os.path.isfile("{} Chapters.txt".format(self.setouput(name))):
						mkvmerge_command.append('--chapter-charset')
						mkvmerge_command.append('UTF-8')
						mkvmerge_command.append('--chapters')
						mkvmerge_command.append("{} Chapters.txt".format(self.setouput(name)))

					self.processhelper.muxer(commands=mkvmerge_command)

			if self.novideo and self.season_amazon:
				pass
			
			else:
				if not 'descriptive' in "{}.mp4".format(self.setouput(name)):
					rename(xml_data=self.processhelper.mediainfo_output(file="{}.mkv".format(self.setouput(name))),
						file="{}.mkv".format(self.setouput(name)),
						source="AMZN",
						group=self.group,
						hdr=self.hdr,
						uhd=self.uhd)

			if not self.keep and self.novideo and self.season_amazon:
				pass
			
			else:
				if not self.keep:
					self.logger.info("Cleaning directory...")
					for files in os.listdir(os.path.dirname(self.setouput(name))):
						if name in files:
							f = self.setouput(files)
							if not f.endswith("mkv"):
								os.remove(f)
				if not self.subs:
					for subtitles in self.subsList:
						if os.path.exists("{} {} {}.srt".format(self.setouput(name), subtitles['lang'], subtitles['track'])):
							os.remove("{} {} {}.srt".format(self.setouput(name), subtitles['lang'], subtitles['track']))

		return data
