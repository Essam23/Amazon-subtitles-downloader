import logging, platform
        
DEFAULTCONFIG = {
    "prime_cookies": 'pv',
    "prime_cookies_ca": 'ca', 
    "amazon_cookies_uk": 'uk',
    "amazon_cookies_us": 'us',
    "amazon_cookies_de": 'de',
    "amazon_cookies_jp": 'jp',
    "privatevpn": {'email': 'kneppedyr@gmail.com', 'pass': 'bias4270' , 'port': '8080'},
    "torgurd": {'email': 'h43e037gn71mino', 'pass': '67O66kIbfde1BJG' , 'port': '6060', 'us_ip': '38.125.55.7', 'uk_ip': '82.129.66.112'},
    "nordvpn": {'email': 'bob.tiffner@gmail.com', 'pass': 't953r751' , 'port': '80'},
    "freeproxy": {},
    'cloudfront': True, 
    'level3': False,
    'akamai': True, 
    'limelight': True, 
    "tmdb": "fd52690af9a91b0a15680be5c1d957e9",
    "tmdb_search": True,
    'codec': "",
    "aria2c": r'pyamazon/Helpers/binaries/aria2c.exe', 
    "mediainfo": r'pyamazon/Helpers/binaries/mediaInfo.exe',
    "mkvmerge": r'pyamazon/Helpers/binaries/mkvmerge.exe',
    "mp4decrypt": r'pyamazon/Helpers/binaries/mp4decrypt.exe',
    "subtitledit": r'pyamazon/Helpers/binaries/SE363/SubtitleEdit.exe',
    "group": "", 
    'redownload_ID': 'Yes',
    'output': None,
    "region": "",
    "bitrate": ""
}


class Config(object):
    def __init__(self):
        self.looger = logging.getLogger(__name__)

    def getConfig(self):
        if platform.system() == "Linux":
            DEFAULTCONFIG['mp4decrypt'] = r'pyamazon/Helpers/binaries/mp4decrypt.exe'
            DEFAULTCONFIG['aria2c'] = r'aria2c'
            DEFAULTCONFIG['mediainfo'] = r'mediainfo'
            DEFAULTCONFIG['ffmpeg'] = r'ffmpeg'
            DEFAULTCONFIG['mkvmerge'] = r'mkvmerge'
            DEFAULTCONFIG['subtitledit'] = r'subtitledit'

        return DEFAULTCONFIG.copy()
