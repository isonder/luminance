import os
import sys
from urllib.request import urlretrieve
import pims


_video_dict = {
    'pr06': {
        'casio-f1': 'https://vhub.org/resources/4212/download/2017-09-26'
                    '_pressure-run06_casio-f1_injection.mp4',
        'rx100v': 'https://vhub.org/resources/4222/download/2017-09-26'
                  '_pressure-run06_sony-rx100v_injection.mp4',
        'pco': 'https://vhub.org/resources/4216/download/2017-09-26'
               '_pressure-run06_pco_injection.mp4'
    }
}


def show(run=True, cam=True, url=False):
    s, ul = "", ""
    if run:
        s += "run   "
        ul += "---   "
    if cam:
        s += "cam   "
        ul += "---   "
    if url:
        s += "url   "
        ul += "---   "
    s += "\n" + ul + "\n"
    for run, v in _video_dict.items():
        for cam, urll in v.items():
            if run:
                s += run + "  "
            if cam:
                s += cam + "  "
            if url:
                s += urll
            s += "\n"
    print(s)


def _videoname(run, cam):
    return run + "_" + cam + ".mp4"


def download_video(run=None, cam=None, url=None, targetbase='data' + os.sep):
    if run is not None:
        try:
            urlretrieve(_video_dict[run][cam], targetbase \
                        + _videoname(run, cam))
        except KeyError:
            print("Got wrong identifier: run: %s, cam: %s" % (run, cam),
                  file=sys.stderr)
    elif url is not None:
        urlretrieve(_video_dict[run][cam], targetbase + _videoname(run, cam))
    else:
        raise ValueError("Missing value: One of run or url have to be given.")


def imgseq(run, cam):
    base = "data%s%s_%s%s" %(os.sep, run, cam, os.sep)
    if not os.path.exists(base):
        if not os.path.exists(base + ".mp4"):
            download_video(run=run, cam=cam)
        os.system('mkdir "%s"' % base)
        os.system('ffmpeg -i "%s" -q:v 1 %s%sframe'
                  % ("data" + os.sep + _videoname(run, cam),
                     base, os.sep) + "%08d.jpg")
    return pims.ImageSequence(base + "*.jpg", as_grey=True)
