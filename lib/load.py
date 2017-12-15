import os
import sys
from urllib.request import urlretrieve
import pims


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
    for run, v in tested_videos.items():
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
            print('Downloading video from %s' % tested_videos[run][cam])
            urlretrieve(tested_videos[run][cam], targetbase
                        + _videoname(run, cam))
        except KeyError:
            print("Got wrong identifier: run: %s, cam: %s" % (run, cam),
                  file=sys.stderr)
    elif url is not None:
        urlretrieve(tested_videos[run][cam], targetbase + _videoname(run, cam))
    else:
        raise ValueError("Missing value: One of run or url have to be given.")


def imgseq(run, cam):
    base = "data%s%s_%s%s" % (os.sep, run, cam, os.sep)
    if not os.path.exists(base):
        if not os.path.exists(base + ".mp4"):
            download_video(run=run, cam=cam)
        vname = _videoname(run, cam)
        print("Converting '%s' to image sequence" % vname)
        os.system('mkdir "%s"' % base)
        os.system('ffmpeg -i "%s" -q:v 1 %s%sframe'
                  % ("data" + os.sep + vname, base, os.sep) + "%08d.jpg")
    return pims.ImageSequence(base + "*.jpg", as_grey=True)


runs = [
    'pr06', 'pr05', 'ir16', 'ir15', 'ir14', 'ir13', 'ir12', 'ir07',
    'ir06', 'ir05', 'ir04', 'ir03'
]


vhub_links = {
    'pr06': {
        'dataset': 'https://vhub.org/resources/4211',
        'casio-f1': {
            'bare': 'https://vhub.org/resources/4212/download/2017-09-26'
                    '_pressure-run06_casio-f1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4213/download/2017-09-26'
                       '_pressure-run06_casio-f1_injection_overlay_p30.mp4'
        },
        'rx100v': {
            'bare': 'https://vhub.org/resources/4222/download/2017-09-26'
                    '_pressure-run06_sony-rx100v_injection.mp4',
            'overlay': 'https://vhub.org/resources/4223/download/2017-09-26'
                       '_pressure-run06_sony-rx100v_injection_overlay_p30.mp4'
        },
        'pco': {
            'bare': 'https://vhub.org/resources/4216/download/2017-09-26'
                    '_pressure-run06_pco_injection.mp4',
            'overlay': 'https://vhub.org/resources/4217/download/2017-09-26'
                       '_pressure-run06_pco_injection_overlay_p30.mp4'
        }
    },
    'pr05': {
        'dataset': 'https://vhub.org/resources/4237',
        'sony-4k2': 'https://vhub.org/resources/4238/download/2017-09-13'
                    '_pressure-run05_sony-4k2_injection.mp4'
    },
    'ir16': {
        'dataset': 'https://vhub.org/resources/4240',
        'casio-f1': {
            'bare': 'https://vhub.org/resources/4241/download/2017-01-21'
                    '_injection-run16_casio-f1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4242/download/2017-01-21'
                       '_injection-run16_casio-f1_injection_overlay_p30.mp4'
        },
        'sony-4k1': 'https://vhub.org/resources/4243/download/2017-01-21'
                    '_injection-run16_sony-4k1_injection.mp4',
        'sony-4k2': 'https://vhub.org/resources/4244/download/2017-01-21'
                    '_injection-run16_sony-4k2_injection.mp4',
        'sony-cx220': 'https://vhub.org/resources/4245/download/2017-01-21'
                      '_injection-run16_sony-cx220_injection.mp4'
    },
    'ir15': {
        'dataset': 'https://vhub.org/resources/4246',
        'casio-f1': {
            'bare': 'https://vhub.org/resources/4252/download/2016-11-27'
                    '_injection-run15_casio-f1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4254/download/2016-11-27'
                       '_injection-run15_casio-f1_injection_overlay_p30.mp4'
        },
        'sony-4k1': {
            'bare': 'https://vhub.org/resources/4253/download/2016-11-27'
                    '_injection-run15_sony-4k1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4255/download/2016-11-27'
                       '_injection-run15_sony-4k1_injection_overlay_p30.mp4'
        },
        'sony-4k2': {
            'bare': 'https://vhub.org/resources/4256/download/2016-11-27'
                    '_injection-run15_sony-4k2_injection.mp4',
            'overlay': 'https://vhub.org/resources/4257/download/2016-11-27'
                       '_injection-run15_sony-4k2_injection_overlay_p30.mp4'
        },
        'sony-cx220': {
            'bare': 'https://vhub.org/resources/4258/download/2016-11-27'
                    '_injection-run15_sony-cx220_injection.mp4',
            'overlay': 'https://vhub.org/resources/4259/download/2016-11-27'
                       '_injection-run15_sony-cx220_injection_overlay_p30.mp4'
        }
    },
    'ir14': {
        'dataset': 'https://vhub.org/resources/4261',
        'casio-f1': {
            'bare': 'https://vhub.org/resources/4262/download/2016-11-09'
                    '_injection-run14_casio-f1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4263/download/2016-11-09'
                       '_injection-run14_casio-f1_injection_overlay_p30.mp4',
        },
        'sony-4k1': {
            'bare': 'https://vhub.org/resources/4264/download/2016-11-09'
                    '_injection-run14_sony-4k1_injection.mp4',
            'overlay': 'https://vhub.org/resources/4265/download/2016-11-09'
                       '_injection-run14_sony-4k1_injection_overlay_p30.mp4'
        },
        'sony-4k2': {
            'bare': 'https://vhub.org/resources/4266/download/2016-11-09'
                    '_injection-run14_sony-4k2_injection.mp4',
            'overlay': 'https://vhub.org/resources/4267/download/2016-11-09'
                       '_injection-run14_sony-4k2_injection_overlay_p30.mp4',
        },
        'sony-cx220': {
            'bare': 'https://vhub.org/resources/4268/download/2016-11-09'
                    '_injection-run14_sony-cx220_injection.mp4',
            'overlay': 'https://vhub.org/resources/4269/download/2016-11-09'
                       '_injection-run14_sony-cx220_injection_overlay_p30.mp4'
        },
    },
    'ir13': {
        'dataset': 'https://vhub.org/resources/4270',
        'casio-f1': 'https://vhub.org/resources/4271/download/2016-11-02'
                    '_injection-run13_casio-f1_injection.mp4'
    },
    'ir12': {
        'dataset': 'https://vhub.org/resources/4279',
        'casio-f1': 'https://vhub.org/resources/4281/download/2016-09-21'
                    '_injection-run12_casio-f1_injection.mp4'
    },
    'ir07': {
        'dataset': 'https://vhub.org/resources/4289',
        'sony-4k1': 'https://vhub.org/resources/4290/download/2016-08-24'
                    '_injection-run07_sony-4k1_injection.mp4',
        'sony-4k2': 'https://vhub.org/resources/4292/download/2016-08-24'
                    '_injection-run07_sony-4k2_injection.mp4'
    },
    'ir06': {
        'dataset': 'https://vhub.org/resources/4293',
        'casio-f1': 'https://vhub.org/resources/4295/download/2016-08-24'
                    '_injection-run06_casio-f1_injection.mp4'
    },
    'ir05': {
        'dataset': 'https://vhub.org/resources/4299',
        'casio-f1': 'https://vhub.org/resources/4300/download/2016-08-12'
                    '_injection-run05_casio-f1_injection.mp4'
    },
    'ir04': {
        'dataset': 'https://vhub.org/resources/4306',
        'casio-f1': 'https://vhub.org/resources/4308/download/2016-08-12'
                    '_injection-run04_casio-f1_injection.mp4'
    },
    'ir03': {
        'dataset': 'https://vhub.org/resources/4313',
        'casio-f1': 'https://vhub.org/resources/4315/download/2016-08-10'
                    '_injection-run03_casio-f1_injection.mp4'
    }
}


tested_videos = {
    'pr06': {'casio-f1': '', 'rx100v': '', 'pco': ''},
    'pr05': {'sony-4k2': ''},
    'ir16': {'casio-f1': ''},
    'ir15': {'casio-f1': ''},
    'ir14': {'casio-f1': ''},
    'ir13': {'casio-f1': ''},
    'ir12': {'casio-f1': ''},
    'ir07': {'sony-4k1': '', 'sony-4k2': ''},
    'ir06': {'casio-f1': ''},
    'ir05': {'casio-f1': ''},
    'ir04': {'casio-f1': ''},
    'ir03': {'casio-f1': ''}
}
for k in runs:
    itm = tested_videos[k]
    for kk in itm.keys():
        sitm = vhub_links[k][kk]
        if isinstance(sitm, dict):
            tested_videos[k][kk] = vhub_links[k][kk]['bare']
        else:
            tested_videos[k][kk] = vhub_links[k][kk]
