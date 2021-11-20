import requests, json, random, os, sys
html_file = 'html.html'
defaults = [
 'us-nyc2.pvdata.host',
 'uk-man.pvdata.host',
 'ca-tor.pvdata.host',
 'it-mil.pvdata.host',
 'fr-par.pvdata.host']

def load_privatevpn():
    PROXY = []
    data = requests.get('https://privatevpn.com/serverlist/', stream=True)
    data = str(data.text)
    data = data.replace('<br>', '')
    with open(html_file, 'w', encoding='utf8') as (file):
        file.write(data)
    with open(html_file, 'r') as (file):
        text = file.readlines()
    if os.path.exists(html_file):
        os.remove(html_file)
    for p in text:
        if 'privatevpn.com' in p or 'pvdata.host' in p and 'https' not in p:
            PROXY.append(p.strip())

    return PROXY


def selector(user, silent=False):
    user_list = []
    load = [
     'ar-bue.pvdata.host', 'au-mel.pvdata.host', 'au-syd.pvdata.host', 'au-syd2.pvdata.host', 'at-wie.pvdata.host', 'be-bru.pvdata.host', 'br-sao.pvdata.host', 'bg-sof.pvdata.host', 'ca-mon.pvdata.host', 'ca-tor.pvdata.host', 'ca-tor2.pvdata.host', 'ca-van.pvdata.host', 'cl-san.pvdata.host', 'co-bog.pvdata.host', 'cr-san.pvdata.host', 'hr-zag.pvdata.host', 'cy-nic.pvdata.host', 'cz-pra.pvdata.host', 'dk-cop.pvdata.host', 'fi-esp.pvdata.host', 'fr-par.pvdata.host', 'de-fra.pvdata.host', 'de-nur.pvdata.host', 'gr-ath.pvdata.host', 'hk-hon.pvdata.host', 'hu-bud.pvdata.host', 'is-rey.pvdata.host', 'in-ban.pvdata.host', 'in-che.pvdata.host', 'id-jak.pvdata.host', 'ie-dub.pvdata.host', 'im-bal.pvdata.host', 'il-tel.pvdata.host', 'it-are.pvdata.host', 'it-mil.pvdata.host', 'it-mil2.pvdata.host', 'jp-tok.pvdata.host', 'jp-tok2.pvdata.host', 'lv-rig.pvdata.host', 'lt-sia.pvdata.host', 'lu-ste.pvdata.host', 'my-kua.pvdata.host', 'mt-qor.pvdata.host', 'mx-mex.pvdata.host', 'md-chi.pvdata.host', 'nl-ams.pvdata.host', 'nz-auc.pvdata.host', 'no-osl.pvdata.host', 'pa-pan.pvdata.host', 'pe-lim.pvdata.host', 'ph-man.pvdata.host', 'pl-tor.pvdata.host', 'pt-lis.pvdata.host', 'ro-buk.pvdata.host', 'ru-kra.pvdata.host', 'ru-mos.pvdata.host', 'ru-pet.pvdata.host', 'rs-bel.pvdata.host', 'sg-sin.pvdata.host', 'sk-bra.pvdata.host', 'za-joh.pvdata.host', 'kr-seo.pvdata.host', 'es-mad.pvdata.host', 'se-got.pvdata.host', 'se-kis.pvdata.host', 'se-sto.pvdata.host', 'ch-zur.pvdata.host', 'ch-zur2.pvdata.host', 'tw-tai.pvdata.host', 'th-ban.pvdata.host', 'tr-ist.pvdata.host', 'uk-lon.pvdata.host', 'uk-man.pvdata.host', 'ua-kie.pvdata.host', 'ua-nik.pvdata.host', 'ae-dub.pvdata.host', 'us-atl.pvdata.host', 'us-buf.pvdata.host', 'us-chi.pvdata.host', 'us-chi2.pvdata.host', 'us-dal.pvdata.host', 'us-las.pvdata.host', 'us-los.pvdata.host', 'us-mia.pvdata.host', 'us-jer.pvdata.host', 'us-nyc.pvdata.host', 'us-nyc2.pvdata.host', 'us-nyc4.pvdata.host', 'us-pho.pvdata.host', 'vn-hoc.pvdata.host']
    if load == []:
        print('no Proxies Found, you may enter wrong code, or search failed!... continue anyway')
        pick_random = random.choice(defaults)
        return pick_random
    else:
        for p in load:
            if p[:2] == user:
                user_list.append(p)

        if user_list == []:
            print('no Proxies Found, you may enter wrong code, or search failed!... continue anyway')
            pick_random = random.choice(defaults)
            return pick_random
        if not silent:
            print(f"Found {str(len(user_list))} Proxies")
            for n, p in enumerate(user_list):
                print(f"[{str(n + 1)}] {p}")

        if silent:
            return random.choice(user_list)
        user_input = input('\nEnter Proxy Number, or Hit Enter for random one: ')
        if user_input == '':
            select = random.choice(user_list)
        else:
            select = user_list[(int(user_input) - 1)]
        return select


class privatevpnAPI(object):

    def privatevpn(code, silentmode=False):
        if silentmode:
            return selector(user=code, silent=True)
        else:
            return selector(user=code, silent=False)