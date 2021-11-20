import json, sys, requests,random

nordvpn_ccode = {'al': '2',
                 'ar': '10', 'au': '13', 'at': '14', 'be': '21', 'ba': '27',
                 'br': '30', 'bg': '33', 'ca': '38', 'cl': '43', 'cr': '52',
                 'hr': '54', 'cy': '56', 'cz': '57', 'dk': '58', 'eg': '64',
                 'ee': '68', 'fi': '73', 'fr': '74', 'ge': '80', 'de': '81',
                 'gr': '84', 'hk': '97', 'hu': '98', 'is': '99', 'in': '100',
                 'id': '101', 'ie': '104', 'il': '105', 'it': '106', 'jp': '108',
                 'lv': '119', 'lu': '126', 'my': '131', 'mx': '140', 'md': '142',
                 'nl': '153', 'nz': '156', 'mk': '128', 'no': '163', 'ro': '179',
                 'pl': '174', 'pt': '175', 'si': '197', 'za': '200', 'kr': '114',
                 'rs': '192', 'sg': '195', 'sk': '196', 'es': '202', 'se': '208',
                 'ch': '209', 'tw': '211', 'th': '214', 'tr': '220', 'ua': '225',
                 'ae': '226', 'gb': '227', 'us': '228', 'vn': '234', 'uk': '227'}


class nordAPI(object):
    def loadcountry(cc):
        if cc.lower() not in nordvpn_ccode:
            print(cc.lower() + ' : not listed in country codes, read country.doc for more info')
            sys.exit()
        else:
            code_country = nordvpn_ccode[cc.lower()]
            cjson = 'https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations&filters={%22country_id%22:' + code_country + '}'
            load_cjson = requests.get(cjson).json()#json.loads(requests.get(cjson).text)
            load_cjson = random.choice(load_cjson)
            pproxy = load_cjson['hostname']
        return pproxy

    def checkproxy():
        try:
            requests.get('https://www.google.com')
        except Exception:
            print('Something went wrong, check proxy authentication.')
            sys.exit()
        dataload = ""
        try:
            ipcheck = requests.get('https://api.myip.com')
            ipload = json.loads(ipcheck.text)
            dataload = 'Location: ' + ipload['ip'] + ' - ' + ipload['country'] + ' - ' + ipload['cc']
        except Exception:
            pass

        return dataload
