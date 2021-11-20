import json, logging, os, sys, re, untangle, humanfriendly
from collections import OrderedDict
from urllib.parse import urlparse
from goto import with_goto

from pyamazon.Configs.config import Config
from pyamazon.Helpers.requesthelper import RequestHelper
from pyamazon.Params import AmazonParameters

urnpssh = "urn:uuid:EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED"

__NAMING_FLAG__ = re.compile(r"([\w]+)")
__NAMING_FLAG_2__ = re.compile(r"(..+:\s)")
__NAMING_FLAG_3__ = re.compile(r"(..+-\s)")


class AmazonParser(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rename = re.compile(r"([\w\d.$-)(]+)")
        self.config = Config()
        self.xraydata = ""
        self.requestor = RequestHelper()
        self.amazonparams = AmazonParameters()

    def spliturls(self, base, extension):
        for x in base:
            try:
                if x['cdn'] == "Cloudfront":
                    return ["{}{}".format(self.urlsplit(x['url']), extension["url"])]
                if x['cdn'] == "Limelight":
                    return ["{}{}".format(self.urlsplit(x['url']), extension["url"])]
                if x['cdn'] == "Akamai":
                    return ["{}{}".format(self.urlsplit(x['url']), extension["url"])]
                if x['cdn'] == "Level3":
                    return ["{}{}".format(self.urlsplit(x['url']), extension["url"])]
            except IndexError:
                continue
        return []

    def urlsplit(self, url):
        return "".join(re.split("(/)(?i)", url)[:-1])

    def cdns(self, apimod):
        mpds = []

        for cdns in apimod:
            if cdns['cdn'] == 'Cloudfront' and self.config.getConfig()["cloudfront"] is True:
                mpds.append(cdns)
            if cdns['cdn'] == 'Level3' and self.config.getConfig()["level3"] is True:
                mpds.append(cdns)
            if cdns['cdn'] == 'Limelight' and self.config.getConfig()["limelight"] is True:
                mpds.append(cdns)
            if cdns['cdn'] == 'Akamai' and self.config.getConfig()["akamai"] is True:
                mpds.append(cdns)

        if len(mpds) == 0:
            raise ValueError("Please modify your config file, turn one of your cdns from false to true and try again!")

        return mpds

    def human_size(self, num_bytes):
        return humanfriendly.format_size(num_bytes, binary=True)

    def get_track_size(self, track_repr):
        file_size = sorted(track_repr['SegmentList']['SegmentURL'], key=lambda surl: int(surl['@mediaRange'].split('-')[1]),
                   reverse=True)[0]['@mediaRange'].split('-')[1]
        return int(file_size)

    def mpds(self, data, type):
        none_sorted_video_urls = []
        none_sorted_audio_urls = []
        audio_unecrypted = False

        toreturn = {}

        if not isinstance(data, list):
            data = [data]
        
        for mpd in data:
            manifesturl = None
            if 'data' in mpd:
                manifesturl = mpd['url']
                mpd = mpd['data']
            for content in mpd['MPD']['Period']['AdaptationSet']:
                ##Video
                if content['@group'] == '2':
                    for videocontent in content['ContentProtection']:
                        if videocontent['@schemeIdUri'] == urnpssh:
                            videopssh = videocontent['cenc:pssh']
                            for videourls in content['Representation']:
                                try:
                                    none_sorted_video_urls.append({
                                        'bitrate': "{0:g} kbps".format(eval(videourls['@bandwidth']) / 1000),
                                        'codec': videourls['@codecs'],
                                        'fr': round(eval(videourls['@frameRate']), 3),
                                        'width': videourls['@width'],
                                        'size': self.get_track_size(videourls),
                                        'size_human': self.human_size(self.get_track_size(videourls)),
                                        'height': videourls['@height'],
                                        'scan': videourls['@scanType'],
                                        'manifest': manifesturl,
                                        'mpd': manifesturl['url'],
                                        'profile': manifesturl['profile'],
                                        'url': videourls['BaseURL']})
                                
                                except Exception:
                                    continue
                #Audio
                if content['@group'] == '1':
                    warning = False
                    try:
                        if content['@audioTrackId'] is None:
                            l = "en"
                            warning = True
                        else:
                            l = content['@audioTrackId']
                    except:
                        l = "en"
                        warning = True

                    try:
                        for audiocontent in content['ContentProtection']:
                            if audiocontent['@schemeIdUri'] == urnpssh:
                                if isinstance(content['Representation'], list):
                                    for audiourls in content['Representation']:
                                        if "mp4" in str(audiourls['@codecs']):
                                            none_sorted_audio_urls.append({
                                                'bitrate': "{0:g} kb/s".format(eval(audiourls['@bandwidth']) / 1000),
                                                'codec': "aac",
                                                'url': audiourls['BaseURL'],
                                                'size': self.get_track_size(audiourls),
                                                'size_human': self.human_size(self.get_track_size(audiourls)),
                                                'lang': l,
                                                'warning': warning
                                            })
                                        else:
                                            none_sorted_audio_urls.append({
                                                'bitrate': "{0:g} kb/s".format(
                                                    eval(audiourls['@bandwidth']) / 1000),
                                                'codec': audiourls['@codecs'],
                                                'url': audiourls['BaseURL'],
                                                'size': self.get_track_size(audiourls),
                                                'size_human': self.human_size(self.get_track_size(audiourls)),
                                                'lang': l,
                                                'warning': warning
                                            })
                                else:
                                    audiourls = content['Representation']
                                    if "mp4" in str(audiourls['@codecs']):
                                        none_sorted_audio_urls.append({
                                            'bitrate': "{0:g} kb/s".format(
                                                eval(audiourls['@bandwidth']) / 1000),
                                            'codec': "aac",
                                            'url': audiourls['BaseURL'],
                                            'size': self.get_track_size(audiourls),
                                            'size_human': self.human_size(self.get_track_size(audiourls)),
                                            'lang': l,
                                            'warning': warning
                                        })
                                    else:
                                        none_sorted_audio_urls.append({
                                            'bitrate': "{0:g} kb/s".format(
                                                eval(audiourls['@bandwidth']) / 1000),
                                            'codec': audiourls['@codecs'],
                                            'url': audiourls['BaseURL'],
                                            'size': self.get_track_size(audiourls),
                                            'size_human': self.human_size(self.get_track_size(audiourls)),
                                            'lang': l,
                                            'warning': warning
                                        })
                    except:
                        self.logger.debug("set audio unecrypted to true")
                        audio_unecrypted = True
                        if isinstance(content['Representation'], list):
                            for audiourls in content['Representation']:
                                none_sorted_audio_urls.append({
                                    'bitrate': "{0:g} kb/s".format(eval(audiourls['@bandwidth']) / 1000),
                                    'codec': audiourls['@codecs'],
                                    'url': audiourls['BaseURL'],
                                    'size': self.get_track_size(audiourls),
                                    'size_human': self.human_size(self.get_track_size(audiourls)),
                                    'lang': l,
                                    'warning': warning
                                })
                        else:
                            audiourls = content['Representation']
                            none_sorted_audio_urls.append({
                                'bitrate': "{0:g} kb/s".format(eval(audiourls['@bandwidth']) / 1000),
                                'codec': audiourls['@codecs'],
                                'url': audiourls['BaseURL'],
                                'size': self.get_track_size(audiourls),
                                'size_human': self.human_size(self.get_track_size(audiourls)),
                                'lang': l,
                                'warning': warning
                            })

        audio_urls = sorted(none_sorted_audio_urls, key=lambda k: float(k['bitrate'].replace('kb/s', '').strip()))
        video_urls = sorted(none_sorted_video_urls, key=lambda k: int(k['size']))
        
        toreturn.update({'audioencrypted': audio_unecrypted})
        toreturn.update({'videourls': video_urls})
        toreturn.update({'audiourls': audio_urls})
        
        self.logger.debug(json.dumps(video_urls, indent=4))
        self.logger.debug(json.dumps(audio_urls, indent=4))

        return toreturn

    def getvideo_size(self, url):
        return self.human_size(self.requestor.getHeaders(url))

    def getvideo(self, manifest, videoquality, display=False, hdr=False):
        video = OrderedDict()
        videoquality = videoquality.replace("p", "").strip()
        x = 0
        for vid in manifest["videourls"]:
            height = vid['height']
            bitrate = vid['bitrate']
            width = vid['width']
            profile = vid['profile']
            size = vid['size_human']
            codec = vid['codec']
            n = vid['mpd'].split('/')[-1]
            url = vid['mpd'].replace(n, vid['url'])

            if display:
                x = x + 1
                self.logger.info(
                    "Video {} - Bitrate: {} | Resolution: {}x{} | Codec: {} | Profile: {} | Size: {}".format(
                        str(x).zfill(2), bitrate, width, height, codec, profile, size))
            
            if hdr: 
                if videoquality == "best" and vid['codec'] == 'hev1.2.4.L120.90':
                    if height not in video:
                        video = vid
                    if height in video and bitrate not in video:
                        video = vid

            else:                                        
                if videoquality == "1080":
                    if int(vid['height']) in range(800, 1081):
                        if height not in video:
                            video = vid
                        if height in video and bitrate not in video:
                            video = vid
                if videoquality == "720":
                    if int(vid['height']) in range(528, 721):
                        if height not in video:
                            video = vid
                        if height in video and bitrate not in video:
                            video = vid
                if videoquality == "best":
                    if height not in video:
                        video = vid
                    if height in video and bitrate not in video:
                        video = vid
                else:
                    if videoquality == vid['height']:
                        if height not in video:
                            video = vid
                        if height in video and bitrate not in video:
                            video = vid

        if display:
            self.logger.info("Selected video:")
            self.logger.info(video)
            exit(1)
        try:
            video["url"]
        except KeyError:
            self.logger.info("This video quality {} does not exist".format(videoquality))
            self.logger.info('Try quality: {}'.format(vid['height']))
            exit(1)
        
        return video

    def getaudio(self, manifest, audioquality, language, display=False, aac=False):
        audios = []
        audio = OrderedDict()
        x = 0
        for lang_input in language:
            for aud in manifest["audiourls"]:
                codec = aud['codec']
                bitrate = aud['bitrate']
                lang = aud["lang"]
                if display:
                    x = x + 1
                    self.logger.info("Audio {} - Bitrate: {} | Codec: {} | Language: {}".format(
                        str(x).zfill(2), bitrate, codec, lang))
                if aac is False:
                    if aud['bitrate'] == "{} kb/s".format(str(audioquality)):
                        if codec not in audio:
                            if lang == lang_input['lang']:
                                audio = aud
                        if codec in audio and bitrate not in audio:
                            if lang == lang_input['lang']:
                                audio = aud
                    elif audioquality == "best":
                        if codec not in audio:
                            if lang == lang_input['lang']:
                                audio = aud
                        if codec in audio and bitrate not in audio:
                            if lang == lang_input['lang']:
                                audio = aud
                if aac:
                    if aud['codec'] == "aac":
                        if aud['bitrate'] == "{} kb/s".format(str(audioquality)):
                            if codec not in audio:
                                audio = aud
                            if codec in audio and bitrate not in audio:
                                audio = aud
                            if codec in audio and bitrate in audio and lang_input['lang'] not in audio:
                                audio = aud
                        elif audioquality == "best":
                            if codec not in audio:
                                audio = aud
                            if codec in audio and bitrate not in audio:
                                audio = aud
                            if codec in audio and bitrate in audio and lang_input['lang'] not in audio:
                                audio = aud

            if len(audio) == 0:
                for aud in manifest["audiourls"]:
                    if aud['bitrate'] == "{} kb/s".format(str(audioquality)):
                        if codec not in audio:
                            if lang == "en":
                                audio = aud
                        if codec in audio and bitrate not in audio:
                            if lang == "en":
                                audio = aud
                    elif audioquality == "best":
                        if codec not in audio:
                            if lang == "en":
                                audio = aud
                        if codec in audio and bitrate not in audio:
                            if lang == "en":
                                audio = aud
            if display:
                self.logger.info("Selected audio")
                self.logger.info(audio)
            try:
                audio["url"]
                audios.append(audio)
            except KeyError:
                self.logger.info("This audio quality {} does not exits".format(audioquality))
                exit(1)
        return audios

    def vcid(self, data):
        try:
            return data["returnedTitleRendition"]["contentId"]
        except KeyError:
            return False

    def parseChapters(self, name):
        chapters = None
        try:
            for widget in self.xraydata["page"]["sections"]["center"]["widgets"]["widgetList"]:
                if widget["tabType"] == "scenesTab":
                    chapters = widget["widgets"]["widgetList"][0]["items"]["itemList"]
                    break

            if chapters is not None:
                for num, chapter in enumerate(chapters, 1):
                    seconds = chapter["trickPlayTimeRange"]["startTime"] / 1000
                    minutes, seconds = divmod(seconds, 60)
                    hours, minutes = divmod(minutes, 60)

                    with open("{} Chapters.txt".format(name), 'a', encoding="utf-8") as writer:
                        writer.write("CHAPTER{num}={time}".format(
                            num=str(num).zfill(2),
                            time='%02d:%02d:%02d.000' % (hours, minutes, seconds)
                        ))
                        writer.write("\n")
                        writer.write('CHAPTER{num}NAME={name}'.format(
                            num=str(num).zfill(2),
                            name=re.sub(r'^\d+\.\s', '', chapter['textMap']['PRIMARY'])
                        ))
                        writer.write("\n")

                self.logger.debug("Done writing chapters to {} Chapters.txt".format(name))

        except KeyError:
            self.logger.info("{} does not have chapters!".format(os.path.basename(name)))

    def ReplaceChapters(self, X):
        pattern1 = re.compile('(?:[A-Z]*)(?:[A-Za-z_ -=]*)( )')
        X = pattern1.sub('', X)
        return X

    def chapters(self, xray_response, type, data):
        ChapterList = []
        from collections import defaultdict
        try:
            for x in xray_response['page']['sections']['center']['widgets']['widgetList']:
                if x['tabType'] == 'scenesTab':
                    for y in x['widgets']['widgetList']:
                        if y['items']['itemList'][0]['blueprint']['id'] == 'XraySceneItem':
                            for z in y['items']['itemList']:
                                ChapterDict = (
                                    z['textMap']['PRIMARY'], self.ReplaceChapters(z['textMap']['TERTIARY']))
                                ChapterList.append(ChapterDict)

            ChaptersList_new = defaultdict(list)
            for ChapterName, ChapterTime in ChapterList:
                ChaptersList_new[ChapterName].append(ChapterTime)

            if str(ChaptersList_new.items()) == 'dict_items([])':
                self.logger.debug("Chapters not available")
            else:
                return ChaptersList_new
        except Exception:
            self.logger.debug("Chapters not available")
        return ChapterList

    @with_goto
    def name(self, xray_response, type, data, skipxray=False):
        if skipxray:
            goto.manual
        label.begin
        if xray_response:
            imdbID = None
            params = self.amazonparams.tmdb_show_params().copy()
            params.update({"language": "en-US"})
            params.update({"external_source": "imdb_id"})
            for outerWidgetList in xray_response.json()['page']['sections']['center']['widgets']['widgetList']:
                for innerWidgetList in outerWidgetList['widgets']['widgetList']:
                    if innerWidgetList.get('items'):
                        for items in innerWidgetList['items']['itemList']:
                            if "title" in items.get('id'):
                                imdbID = items['id'].split('/')[2]
                                break

            if imdbID is None:
                self.logger.debug("unable to find a imdb ID, going to manual")
                goto.manual
            xray_response = self.requestor.getItems(
                url="https://api.themoviedb.org/3/find/{}".format(imdbID),
                params=params
            )
            if xray_response.status_code == 200:
                xray_response = xray_response.json()
                name_return = None
                if type == "EPISODE":
                    if not len(xray_response['tv_episode_results']):
                        goto.manual
                    episode_name = xray_response['tv_episode_results'][0]["name"]
                    episode_number = str(xray_response['tv_episode_results'][0]["episode_number"]).zfill(2)
                    season_number = str(xray_response['tv_episode_results'][0]["season_number"]).zfill(2)
                    overview = xray_response['tv_episode_results'][0]["overview"]

                    name_return = "{} S{}E{} {}".format(
                        str(data['debug']['catalogMetadata']['family']['tvAncestors'][1]['catalog']['title']).replace(',', ''),
                        season_number,
                        episode_number,
                        episode_name
                    )
                    name_return = name_return

                if type == "MOVIE":
                    if xray_response.get('movie_results') != []:
                        name = xray_response['movie_results'][0]["original_title"]
                        year = str(xray_response['movie_results'][0]["release_date"]).split("-")[0]
                        name = name
                        name_return = "{} {}".format(name, year)
                        self.logger.debug("Returning name: {}".format(name_return))
                    goto.manual
                return name_return
        else:
            label.manual
            self.logger.debug("Response from xray was invalid, doing it manually")

            type = data['debug']['catalogMetadata']['catalog']['type']

            if not type:
                self.logger.info("Something went wrong with the download portion of the manifest, please inspect")
                self.logger.info(json.dumps(data, indent=4))

            return self.__tmdb(data=data, type=type, skip_xray=skipxray)

    def __tmdb(self, data, type, skip_xray):
        
        if skip_xray:
            if type == "EPISODE":
                name_of_show = data['debug']['catalogMetadata']['family']['tvAncestors'][1]['catalog']['title']
                name_of_episode = data['debug']['catalogMetadata']['catalog']['title']
                episode_number = str(data['debug']['catalogMetadata']['catalog']['episodeNumber']).zfill(2)
                season_number = str(data['debug']['catalogMetadata']['family']['tvAncestors'][0]['catalog']['seasonNumber']).zfill(2)
                self.logger.debug("Pre RE: {}".format(name_of_episode))
                name_of_episode = __NAMING_FLAG_2__.sub("", name_of_episode)
                self.logger.debug("Post RE: {}".format(name_of_episode))
                name_of_episode = name_of_episode.replace("/", " and ")
                name_of_episode = name_of_episode
                return '{} S{}E{} {}'.format(name_of_show, season_number, episode_number, name_of_episode)

        original = self.amazonparams.tmdb_show_params().copy()

        if type == "EPISODE":
            name_of_show = data['debug']['catalogMetadata']['family']['tvAncestors'][1]['catalog']['title']
            name_of_episode = data['debug']['catalogMetadata']['catalog']['title']
            episode_number = data['debug']['catalogMetadata']['catalog']['episodeNumber']
            season_number = data['debug']['catalogMetadata']['family']['tvAncestors'][0]['catalog']['seasonNumber']

            params = original.copy()
            params.update({"query": name_of_show})
            self.logger.debug("Post RE: {}".format(name_of_episode))
            name_of_episode = __NAMING_FLAG_2__.sub("", name_of_episode)
            self.logger.debug("Post RE: {}".format(name_of_episode))
            name_of_episode = name_of_episode.replace("/", " and ")
            name_of_episode = name_of_episode

            seasonID = self.requestor.getItems(url="https://api.themoviedb.org/3/search/tv", params=params).json()
            
            if len(str(season_number)) == 3:
                season_number = list(str(season_number))[0]
            if len(seasonID['results']) == 0:
                episode_number = str(data['debug']['catalogMetadata']['catalog']['episodeNumber']).zfill(2)
                season_number = str(data['debug']['catalogMetadata']['family']['tvAncestors'][0]
                                    ['catalog']['seasonNumber']).zfill(2)

                return '{} S{}E{} {}'.format(name_of_show, season_number, episode_number, name_of_episode)
            
            if seasonID.get('results'):
                episode_data = self.requestor.getItems(
                    url="https://api.themoviedb.org/3/tv/{}/season/{}".format(seasonID['results'][0]['id'], season_number), params=original)
                if episode_data:
                    episode_data = episode_data.json()
                    for episodes in episode_data.get('episodes'):
                        if episode_number == episodes['episode_number']:
                            e = str(episodes['episode_number']).zfill(2)
                            s = str(episodes['season_number']).zfill(2)
                            n = str(episodes['name']).replace(')', '').replace('(', 'Part ').replace("/", " and ")
                            n = __NAMING_FLAG_2__.sub('', n)
                            name_to_return = '{} S{}E{} {}'.format(name_of_show, s, e, n)
                            return name_to_return
                    else:
                        episode_number = str(data['debug']['catalogMetadata']['catalog']['episodeNumber']).zfill(2)
                        season_number = str(data['debug']['catalogMetadata']['family']['tvAncestors'][0]
                                            ['catalog']['seasonNumber']).zfill(2)

                    return '{} S{}E{} {}'.format(name_of_show, season_number, episode_number, name_of_episode)
                else:
                    episode_number = str(data['debug']['catalogMetadata']['catalog']['episodeNumber']).zfill(2)
                    season_number = str(data['debug']['catalogMetadata']['family']['tvAncestors'][0]
                                        ['catalog']['seasonNumber']).zfill(2)

                    return '{} S{}E{} {}'.format(name_of_show, season_number, episode_number, name_of_episode)
        
        if type == "MOVIE":
            name_of_movie = data['debug']['catalogMetadata']['catalog']['title']
            params = original.copy()
            params.update({"query": name_of_movie, "language": "en-US", "include_adult": "false"})
            tmdb_result = self.requestor.getItems(url='https://api.themoviedb.org/3/search/movie', params=params)
            if tmdb_result.status_code == 200:
                data = tmdb_result.json()
                if len(data['results']) == 1:
                    name = data['results'][0]['title']
                    try:
                        year = str(data['results'][0]['release_date']).split("-")[0]
                    except Exception:
                        year = ''
                    return '{} {}'.format(name, year)
                else:
                    self.logger.info('Unable to find movie from tmdb, or multiple results')
                    return name_of_movie

            raise ValueError('status code is not 200, please inspect\n{}'.format(data.content))

