"""
these are base urls for amazon api end points for different regions
"""
import hashlib

AMZONREGIONS = {
    "us": {
        "url": "atv-ps.amazon.com",
        "marketplaceID": "ATVPDKIKX0DER",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": False
    },
    "uk": {
        "url": "atv-ps-eu.amazon.co.uk",
        "marketplaceID": "A1F83G8C2ARO7P",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": False
    },
    "de": {
        "url": "atv-ps-eu.amazon.de",
        "marketplaceID": "A1PA6795UKMFR9",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": False
    },
    "pv": {
        "url": "atv-ps-eu.primevideo.com",
        "marketplaceID": "A3K6Y4MI8GDYMT",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": True
    },
    "ca": {
        "url": "atv-ps.primevideo.com",
        "marketplaceID": "ART4WZ8MWBX2Y",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": True
    },
    "jp": {
        "url": "atv-ps-fe.amazon.co.jp",
        "marketplaceID": "A1VC38T7YXB528",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": False
    },
    "in": {
        "url": "atv-ps-eu.primevideo.com",
        "marketplaceID": "A2MFUE2XK8ZSSY",
        "customerId": "A18CCOQSEH5B6B",
        "token": "dc080fd66f01cbcb73751fd8c12b8832",
        "clientId": "f22dbddb-ef2c-48c5-8876-bed0d47594fd",
        "primevideo": True
    }

}

"""
NO NEED TO LOOK OR MODIFY FURTHER THAN HERE!!!!
"""
AMZN_PARAMS_URL = "https://{base_url}/cdp/catalog/GetPlaybackResources"
AMZN_BROWSE_URL = "https://{base_url}/cdp/catalog/Browse"
PRIME_BROWSE_URL = "https://{base_url}/detail/{asin}"
AMZN_CHAPTER_URL = "https://{base_url}/cdp/catalog/GetASINDetails"
AMZN_VIDEO_INFO_URL = "https://{base_url}/cdp/catalog/GetPlaybackResources?asin={asin}&consumptionType=Streaming&desiredResources=AudioVideoUrls%2CCatalogMetadata%2CPlaybackSettings%2CSubtitleUrls%2CForcedNarratives&deviceID={device_id}&deviceTypeID={device_type_id}&firmware=1&marketplaceID={marketplace_id}&resourceUsage=ImmediateConsumption&videoMaterialType=Feature&deviceDrmOverride=CENC&deviceStreamingTechnologyOverride=DASH&deviceProtocolOverride=Https&supportedDRMKeyScheme=DUAL_KEY&operatingSystemName=Windows&operatingSystemVersion=10.0&customerID={customer_id}&token={token}&deviceBitrateAdaptationsOverride={bitrate}&audioTrackId=all&playbackSettingsFormatVersion=1.0.0&titleDecorationScheme=primary-content&{hevc}&gascEnabled={gasc}{uhd}"
AMZN_LICENSE_URL = "https://{base_url}/cdp/catalog/GetPlaybackResources?asin={asin}&consumptionType=Streaming&desiredResources=Widevine2License&deviceID={device_id}&deviceTypeID={device_type_id}&firmware=1&marketplaceID={marketplace_id}&resourceUsage=ImmediateConsumption&videoMaterialType=Feature&operatingSystemName=Windows&operatingSystemVersion=10.0&customerID={customer_id}&token={token}&deviceDrmOverride=CENC&deviceStreamingTechnologyOverride=DASH&gascEnabled={gasc}"
AMAZON_XRAY_URL = 'https://{base_url}/swift/page/xray'

AMAZON_XRAY_PARAMS = {
    'firmware': '1',
    'format': 'json',
    'deviceID': '1',
    'deviceTypeID': 'AOAGZA014O5RE',
    'marketplaceId': '',
    'decorationScheme': 'none',
    'version': 'inception-v2',
    'featureScheme': 'INCEPTION_LITE_FILMO_V2',
    'pageType': 'xray',
    'pageId': 'fullScreen',
    'serviceToken': {
        'consumptionType': 'Streaming',
        'deviceClass': 'normal',
        'playbackMode': 'playback',
        'vcid': ''
    },
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
AMAZON_DEVICE_ID = hashlib.sha224(("CustomerID" + USER_AGENT).encode('utf-8')).hexdigest()
AMAZON_DEVICE_TYPE_ID = "AOAGZA014O5RE"

AMAZON_VIDEO_INFO_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Origin": "https://www.amazon.com"
}

AMAZON_LICENSE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Origin": "https://www.amazon.com"
}

AMAZON_MP4_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Origin": "https://www.amazon.com",
    "Connection": "keep-alive",
    "DNT": "1",
    "Range": "bytes=0-"
}

WIDEVINE_PSSH_URN = 'urn:uuid:EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED'

class AmazonConfig(object):
    def xray(self, vcid, cookies, baseurl):
        import json
        import requests
        params = AMAZON_XRAY_PARAMS.copy()
        params["serviceToken"]["vcid"] = vcid
        params["serviceToken"] = json.dumps(params["serviceToken"])
        url = AMAZON_XRAY_URL.format(
            base_url=baseurl
        )
        data = requests.get(url=url, cookies=cookies, params=params).json()

        return data
