import logging, os, platform, re, subprocess, untangle
from pyamazon.Configs.config import Config

__LOGGER__ = logging.getLogger(__name__)

def rename(xml_data, file, source, group, hdr, uhd):

    try:
        base_name = file
        name = os.path.splitext(os.path.basename(file))[0]
        directory_name = os.path.dirname(file)
        media = untangle.parse(xml_data)
        videoroot = None
        audioroot = None
        if group is None:
            group = Config().getConfig()["group"]

        for root in media.MediaInfo.media.track:
            if root['type'] == 'Video':
                videoroot = root
            if root['type'] == 'Audio':
                audioroot = root

        if int(videoroot.Width.cdata) == 1280 or int(videoroot.Height.cdata) == 720:
            resolution = '720p'
        elif int(videoroot.Width.cdata) == 1920 or int(videoroot.Height.cdata) == 1080:
            resolution = "1080p"
        else:
            resolution = '{}p'.format(videoroot.Height.cdata)

        if "E-AC-3" in audioroot.Format.cdata:
            audioCodec = "DD+"
        elif "AC-3" in audioroot.Format.cdata:
            audioCodec = "DD"
        elif "AAC" in audioroot.Format.cdata:
            audioCodec = "AAC"
        else:
            __LOGGER__.warning("No Audio Root Found: {}".format(audioroot.Format.cdata))
            audioCodec = None

        if "6" in audioroot.Channels.cdata:
            channels = "5.1"
        elif "2" in audioroot.Channels.cdata:
            channels = "2.0"
        elif "1" in audioroot.Channels.cdata:
            channels = "1.0"
        else:
            __LOGGER__.warning("No Audio Channel Found: {}".format(audioroot.Channels.cdata))
            channels = None

        if hdr or uhd:
            codec = 'x265.10bit.HDR'
        else:
            if videoroot.Format.cdata == "AVC":
                codec = "x264"
            elif videoroot.Format.cdata == "HEVC":
                codec = "x265"
        #else:
        #    __LOGGER__.info(videoroot.Format.cdata)
        #    codec = None

        name = name.replace(" ", ".").replace("'", "").replace(',', '')
        name = '{}.{}.{}.WEB-DL.{}{}.{}-{}'.format(
            name, resolution, source, audioCodec, channels, codec, group
        )
        #name = re.match(r'([\w\d.$)(-]+)', name).group()
        name = re.sub(r'(\.\.)', '.', name)
        filename = '{}.mkv'.format(os.path.join(directory_name, name))
        if os.path.exists( filename ):
            os.remove(filename)

        os.rename(base_name, filename)
        __LOGGER__.debug("Renamed: {} to {}.mkv".format(
            base_name, os.path.join(directory_name, name)
        ))
        #__LOGGER__.info("Renaming Done...")

    except AttributeError:
        __old_mediainfo__(media, file, source)

def __old_mediainfo__(media, file, source):
    base_name = file
    name = os.path.splitext(os.path.basename(file))[0]
    directory_name = os.path.dirname(file)
    video_root = None
    audio_root = None

    for roots in media.Mediainfo.File.track:
        if roots['type'] == "Video":
            video_root = roots
        if roots['type'] == "Audio":
            audio_root = roots

    if "720" in video_root.Width.cdata or "720" in video_root.Height.cdata:
        resolution = '720p'
    elif "1 920" in video_root.Width.cdata or "1 080" in video_root.Height.cdata:
        resolution = "1080p"
    else:
        resolution = '{}p'.format(video_root.Height.cdata)

    if "E-AC-3" in audio_root.Format.cdata:
        audioCodec = "DDP"
    elif "AC-3" in audio_root.Format.cdata:
        audioCodec = "DD"
    elif "AAC" in audio_root.Format.cdata:
        audioCodec = "AAC"
    else:
        __LOGGER__.warning("No Audio Root Found: {}".format(audio_root.Format.cdata))
        audioCodec = None

    if "6" in audio_root.Channel_s_.cdata:
        channels = "5.1"
    elif "2" in audio_root.Channel_s_.cdata:
        channels = "2.0"
    elif "1" in audio_root.Channel_s_.cdata:
        channels = "1.0"
    else:
        __LOGGER__.warning("No Audio Channel Found: {}".format(audio_root.Channels.cdata))
        channels = None

    if video_root.Format.cdata == "AVC":
        codec = "H.264"
    elif video_root.Format.cdata == "HEVC":
        codec = "H.265"
    else:
        __LOGGER__.warning(video_root.Format.cdata)
        codec = None

    name = name.replace(" ", ".").replace("'", "").replace(',', '')
    name = '{}.{}.{}.WEB-DL.{}{}.{}-{}'.format(
        name, resolution, source, audioCodec, channels, codec, Config().getConfig()["group"]
    )
    name = re.match(r'([\w\d.$)(-]+)', name).group()
    name = re.sub(r'(\.\.)', '.', name)

    os.rename(base_name, '{}.mkv'.format(os.path.join(directory_name, name)))
    __LOGGER__.debug("Renamed: {} to {}.mkv".format(
        base_name, os.path.join(directory_name, name)
    ))
    #__LOGGER__.info("Renaming Done...")
