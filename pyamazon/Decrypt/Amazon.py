import base64, logging, time, json, sys
import pyamazon.Configs.Amazon as config
import pyamazon.Configs.config as universal
from pyamazon.Helpers.requesthelper import RequestHelper
from pyamazon.Decrypt.wvdecrypt import WvDecrypt

class AmazonDecrypt(object):
	def __init__(self, asin, region='us', profile=None):
		self.asin = asin
		self.region = region
		self.profile = profile
		self.config = config
		self.logger = logging.getLogger(__name__)
		self.requesthelper = RequestHelper()
		if region == 'pv' or region == 'in' or region == 'ca':
			self.gasc = True
		else:
			self.gasc = False

	def do_decrypt(self, config):
		wvdecrypt = WvDecrypt(init_data_b64=config['init_data_b64'], cert_data_b64=config['cert_data_b64'])
		chal = wvdecrypt.get_challenge()
		license_b64 = self.get_license(chal)
		if license_b64 == None:
			print('Error!')
			return []
		else:
			wvdecrypt.update_license(license_b64)
			Correct, keyswvdecrypt = wvdecrypt.start_process()
			if Correct:
				return keyswvdecrypt
			else:
				return []

	def get_amazon_license_req(self, asin, region='us'):
		url = self.config.AMZN_LICENSE_URL.format(
			base_url=self.config.AMZONREGIONS[region]["url"],
			asin=asin,
			device_id=self.config.AMAZON_DEVICE_ID,
			device_type_id=self.config.AMAZON_DEVICE_TYPE_ID,
			marketplace_id=self.config.AMZONREGIONS[region]["marketplaceID"],
			customer_id=self.config.AMZONREGIONS[region]['customerId'],
			token=self.config.AMZONREGIONS[region]['token'],
			gasc=self.gasc
		)

		headers = self.config.AMAZON_LICENSE_HEADERS
		headers['Origin'] = "https://{0}".format(self.config.AMZONREGIONS[region]["url"])
		return {'url': url, 'headers': headers}

	def get_license(self, challenge):
		self.logger.debug("doing license request")
		license_req_data = self.get_amazon_license_req(self.asin, self.region)
		url = license_req_data['url']
		headers = license_req_data['headers']
		cert_request_encoded = base64.b64encode(challenge)
		cert_request_form_data = {
			"widevine2Challenge": cert_request_encoded,
			"includeHdcpTestKeyInLicense": "true"}
		
		i = 0
		while i < 1:
			try:
				self.logger.debug("Getting cert")
				cert_res = self.requesthelper.postItems(url=url, headers=headers, user=self.profile, data=cert_request_form_data)
				break
			except Exception as e:
				self.logger.debug(e)
				time.sleep(5)
				i = i + 1
				continue
		try:
			cert_res_json = json.loads(cert_res.text)
			cert_base64 = cert_res_json['widevine2License']['license']
		
		except KeyError:
			#self.logger.error("License Acquisition failed!")
			#self.logger.error('\n{}'.format(cert_res_json))
			return
		
		self.logger.debug("license acquired")
		return cert_base64
