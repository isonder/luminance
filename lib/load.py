import os
import sys
from urllib.request import urlretrieve


_video_dict = {
    'pr06': {
        'casio-f1': 'https://vhub.org/resources/4212/download/2017-09-26_pressure-run06_casio-f1_injection.mp4',
        'rx100v': 'https://vhub.org/resources/4222/download/2017-09-26_pressure-run06_sony-rx100v_injection.mp4',
        'pco': 'https://vhub.org/resources/4216/download/2017-09-26_pressure-run06_pco_injection.mp4'
    }
}
videos = list(_video_dict.keys())


def _videoname(run, cam):
    return run + "_" + cam + ".mp4"


def download_video(run=None, cam=None, url=None, targetbase='data' + os.sep):
    if run is not None:
        try:
            urlretrieve(_video_dict[run][cam], targetbase + _videoname(run, cam))
        except KeyError:
            print("Got wrong identifier: run: %s, cam: %s" % (run, cam), file=sys.stderr)
    elif url is not None:
        urlretrieve(_video_dict[run][cam], targetbase + _videoname(run, cam))
    else:
        raise ValueError("Missing value: One of run or url have to be given.")
