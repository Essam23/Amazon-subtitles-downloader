"""
requester helper class, it will handle all requests
"""

import json, logging, os, requests, urllib.parse, html, http.cookiejar

class RequestHelper(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def getcookies(self, user):
        try:
            cookieFile = "cookies/{}.txt".format(user)
            cj = http.cookiejar.MozillaCookieJar(cookieFile)
            cj.load()
            cookies = {}
            for cookie in cj:
                cookie.value = urllib.parse.unquote(html.unescape(cookie.value))
                cookies[cookie.name] = cookie.value
            return cookies

        except FileNotFoundError:
            self.logger.info("The user: [{}] does not exist under cookies/{} folder".format(user, user))
            exit(1)

    def getHeaders(self, url, user=None):
        data = requests.get(url=url, stream=True, cookies=self.getcookies(user) if user is not None else None)
        if data.status_code == 200:
            return int(data.headers['Content-length'])
        else:
            return 0

    def getItems(self, url, params=None, data=None, json_data=None, headers=None, proxies=None, user=None):

        data = requests.get(url=url, params=params, data=data, json=json_data, headers=headers, proxies=proxies,
            cookies=self.getcookies(user) if user is not None else None)
        Jdata = json.dumps(data.text)
        #with open('cc.txt', 'a', encoding='utf-8') as handler:
        #    handler.write(data.text)
        if data.status_code == 200:
            try:
                return data
            except:
                return data

        return False

    def __item_display(self, info):
        self.logger.debug(json.dumps(info, indent=4))

    def postItems(self, url, params=None, data=None, json_data=None, headers=None, proxies=None, user=None,
                  cookies=None):

        data = requests.post(url=url, params=params, data=data, json=json_data, headers=headers,
        cookies=self.getcookies(user) if user is not None else cookies, proxies=proxies)
        if data.status_code in [200, 201]:
            return data
        return False
