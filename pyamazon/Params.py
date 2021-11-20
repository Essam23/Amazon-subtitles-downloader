import json, html, os, urllib.parse, http.cookiejar, logging, sys
from pyamazon.Configs.config import Config

class AmazonParameters(object):
	def __init__(self, *kwargs):				
		self.logger = logging.getLogger(__name__)
		self.tmdbendpoints={"find":"https://api.themoviedb.org/3/find"}
		self.regions = {
			"us":{
				"url":"atv-ps.amazon.com",
				"marketplaceID":"ATVPDKIKX0DER"
			},
			"uk":{
				"url":"atv-ps-eu.amazon.co.uk",
				"marketplaceID" : "A1F83G8C2ARO7P"
			},
			"de":{
				"url":"atv-ps-eu.amazon.de",
				"marketplaceID":"A1PA6795UKMFR9"
			},
			"jp":{
				"url":"atv-ps-fe.amazon.co.jp",
				"marketplaceID": "A1VC38T7YXB528"
			},
			"pv":{
				"url": "atv-ps-eu.primevideo.com",
				"marketplaceID": "A3K6Y4MI8GDYMT",
			},
			"ca":{
				"url": "atv-ps.primevideo.com",
				"marketplaceID": "ART4WZ8MWBX2Y",
			},			
			"in":{
				"url": "atv-ps-eu.primevideo.com",
				"marketplaceID": "A3K6Y4MI8GDYMT",
			}

		}

	def browseparams(self, asin, marketplaceID):
		params = {
			"format":"json",
			"formatVersion":"3",
			"IncludeAll":"T",
			"AID":"T",
			"marketplaceID": marketplaceID,
			"version":"2",
			"SeasonAsin":asin,
			"deviceID":"",
			"deviceTypeID":"AOAGZA014O5RE",
			"firmware":"1",
			"NumberOfResults":"300",
		}

		return params

	def apiparams(self, asin, auth, region, cache, codec, user):

		data = {'asin': asin, 'auth': auth, 'use_cache': cache, 'codec': codec, 'region': region,
			'cookies': json.dumps(self.__getcookies(user))}		
		return data

	def __getcookies(self,user):
		try:
			cookieFile = "cookies/{}.txt".format(user)

			cj = http.cookiejar.MozillaCookieJar(cookieFile)
			cj.load()
			cookies = {}
			for cookie in cj:
				cookie.value = urllib.parse.unquote(
					html.unescape(cookie.value)
				)
				cookies[cookie.name] = cookie.value
			return cookies

		except FileNotFoundError:
			self.logger.info("The user: [{}] does not exist under cookies/{} folder".format(user,user))
			exit(1)

	def vcid_params(self, vcid, region, chapterslang):

		items = {}
		params={
			'firmware': '1',
			'format': 'json',
			'deviceID': '1',
			'deviceTypeID': 'AOAGZA014O5RE',
			'marketplaceId': self.regions[region]["marketplaceID"],
			'decorationScheme': 'none',
			'version': 'inception-v2',
			'featureScheme': 'INCEPTION_LITE_FILMO_V2',
			'pageType': 'xray',
			'uxLocale': chapterslang,
			'pageId': 'fullScreen',
			'serviceToken': {
				'consumptionType': 'Streaming',
				'deviceClass': 'normal',
				'playbackMode': 'playback',
				'vcid':""
			},
		}
		params['serviceToken']['vcid'] = vcid
		params['serviceToken'] = json.dumps(params['serviceToken'])
		items.update({
			"params":params,
			"url":'https://{}/swift/page/xray'.format(self.regions[region]["url"])
		})
		
		return items

	def tmdb_params(self, api_key: str, imdb_id: str):
		items = {}
		params={
			"api_key":api_key,
			"language":"en-US",
			"external_source": "imdb_id"
		}

		items.update({
			"url":"{}/{imdb_id}".format(self.tmdbendpoints['find']),
			"params":params
		})

		return items

	def tmdb_show_params(self):
		#items = {}
		params = {
			"api_key":Config().getConfig()["tmdb"]
		}

		return params