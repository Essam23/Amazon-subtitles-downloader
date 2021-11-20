import argparse, sys, os
from pyamazon.asin_handler import Amazon

def main():
    parser = argparse.ArgumentParser(description='>>> Amazon Downloader v2.0 by ahmed<<<')
    parser.add_argument("-a", "--asin", '--url', dest="asin", help="Specify ASIN or URL to download", required=True)
    parser.add_argument("-sa", "--season-amazon", dest="season_amazon", action="store_true",help="Download Whole season by season ASIN or URL")
    parser.add_argument("-r", "--region", dest="region", help="Specify region [us, ca, pv, uk, de, jp]", required=True)
    parser.add_argument("-p", "--profile", dest="profile", help="Specify profile that match region [us, ca, pv, uk, de]", required=True)
    parser.add_argument("--proxy", "--vpn", dest="proxy", help="Specify proxy from [privatevpn, nordvpn, torgurd, free]")
    parser.add_argument('-pc', '--proxy-code', action='store', dest='proxycode', help='add country for loading proxies', default=0)
    parser.add_argument('-pi', '--proxy-ip', action='store', dest='proxyip', help='add proxy.', default=0) 
    parser.add_argument('-pp', '--proxy-port', action='store', dest='proxyport', help='to force set proxy port', default=0)
    parser.add_argument('-pt', '--proxy-type', action='store', dest='proxytype', help='to force set proxy type', default=0)
    parser.add_argument("-s", "--season", dest="numbered_season", help="Start Downloading from specific season number")
    parser.add_argument("-e", "--episode", dest="episode", help="start from episode or episode range like (-e 3-5)")
    parser.add_argument("--alang", dest="audio_language", type=lambda x: x.split(','), help="Specify language for audio (en or en,fr,it,pl)")
    parser.add_argument("--original", dest="original", action="store_true", help="if set, download the default audio only")
    parser.add_argument("--noAD", dest="noAD", action="store_true", help="if set, No AD download.")
    parser.add_argument('--default-audio-mux', action='store', dest='default_audio_mux', help='set default audio language mux', default=0)
    parser.add_argument('--default-sub-mux', action='store', dest='default_sub_mux', help='set default sub language mux', default=0)
    parser.add_argument("--slang", dest="sub_language", type=lambda x: x.split(','), default=[],help="Specify language for subtitles (en or en,fr,it,pl)")
    parser.add_argument("--others", dest="sub_others", action='store_true', help="add sets + data")
    parser.add_argument("--flang", dest="forced", type=lambda x: x.split(','), default=[],help="Specify language for forced subtitles (en or en,fr,it,pl)")
    parser.add_argument("--subs", dest="subs", action="store_true", help="if set, Download subs only and exit")
    parser.add_argument('--clang', '--chapters-language', dest='chapterslang', help='Specify language for Chapters, esp with primevideo',default=[0])
    parser.add_argument("--nosubs", '--ns', dest="nosubs", action="store_true", help="if set, Subs wont be downloaded")
    parser.add_argument("--novideo", '--nv', dest="novideo", action="store_true", help="if set, Video wont be downloaded")
    parser.add_argument("--noaudio", '--na', dest="noaudio", action="store_true", help="if set, Audio wont be downloaded")        
    parser.add_argument("--nochapters", '--nc', dest="nochapters", action="store_true", help="if set, Chapters wont be downloaded")        
    parser.add_argument("-q", "--quality", dest="quality", help="Specify video quality, default is best [The higest bitrate], you can download like this too (-q 576,720,1080) use it with option --keep")
    parser.add_argument("-qv", '--video-quality', dest="video_quality", help="choose a specific video quality")
    parser.add_argument("-qa", "--audio-quality", dest="audio_quality", help="Specify audio quality, default is best [The higest bitrate], (-qa 128, 192, 224, 256, 384, 448, 640)")
    parser.add_argument("--uhd", dest="hdr", action="store_true", help="Download 4k HDR, only for 4k HDR titles")
    parser.add_argument("--hdr", dest="hdr1080", action="store_true", help="Download 1080 HDR, only for hdr titles")
    parser.add_argument("--hevc", dest="hevc", action="store_true", help="Download HEVC H265, only if title has hevc profile")      
    parser.add_argument("-f", "--file", dest="file", help="Load ASINs from text file (-a None -f asins.txt) asin for each line.")
    parser.add_argument("-gr", "--group", dest="group", help="specify tag for release", default=0)
    parser.add_argument("--sr", "--simple-rename", dest="simple_rename", action="store_true", help="simple renaming, skip tmdb renaming")
    parser.add_argument("--overwrite", dest="overwrite", action="store_true", help="overrides the current item in cache [license option]")
    parser.add_argument("--keys", '--only-keys', '-key', dest="keys", action="store_true", help="show keys")
    parser.add_argument("--info", '-i', dest="links", action="store_true", help="Display info only")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="change log level to debug")  
    parser.add_argument('-o', '--output', dest="output", help='temporarily change the output folder')
    parser.add_argument("--keep", '--no-mux', dest="keep", action="store_true", help="Keep original files.")
    parser.add_argument("--size", dest="size", action="store_true", help="Check file size.")
    parser.add_argument('-c', '--codec', default='H264', choices=['H264', 'H265'], help='video type to download')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(-1)

    folders = ["output", "cookies"]

    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

    amazon = Amazon(vars(parser.parse_args()))
    amazon.runamazon()


if __name__ == '__main__':
    main()