import os
import sys
from urllib.request import urlretrieve
import pims
import numpy
import zipfile
import warnings


show_warnings = True


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
    for rrun, v in tested_videos.items():
        for ccam, urll in v.items():
            if run:
                s += rrun + "  "
            if cam:
                s += ccam + "  "
            if url:
                s += " , ".join(urll) if isinstance(urll, list) else urll
            s += "\n"
    print(s)


def _videoname(run, cam):
    return run + "_" + cam + ".mp4"


def download_dataset(run=None, cam=None, targetbase='data' + os.sep):
    if not os.path.exists(targetbase):
        os.makedirs(targetbase, exist_ok=True)
    try:
        urls = tested_videos[run][cam]
        if isinstance(urls, str):
            urls = [urls]
        ret = []
        for rl in urls:
            trg = targetbase + rl[rl.rfind("/") + 1:]
            if not os.path.exists(trg):
                print('Downloading video from %s to %s' % (rl, trg))
                urlretrieve(rl, trg)
            ret.append(trg)
        return ret
    except KeyError:
        print("Got wrong identifier: run: %s, cam: %s" % (run, cam),
              file=sys.stderr)
        raise


def convert_video_to_imgseq(vname, base):
    print("Converting '%s' to image sequence" % vname)
    if not os.path.exists(base):
        os.makedirs(base, exist_ok=True)
    os.system('ffmpeg -i "%s" -q:v 1 %s%sframe'
              % ("data" + os.sep + vname, base, os.sep) + "%08d.jpg")


def unarchive_imgseq(src, base):
    for s in src:
        with zipfile.ZipFile(s) as archive:
            trg = base[:base.find(os.sep)]
            print("Extracting %d images from '%s' to '%s'"
                  % (len(archive.filelist), s, trg))
            archive.extractall(path=trg)


img_format_labels = [
    'jpg', 'jpeg', 'JPG', 'JPEG',
    'tif', 'tiff', 'TIF', 'TIFF'
]


class ImageFormatError(Exception):
    pass


def imgseq(run, cam):
    base = "data%s%s_%s%s" % (os.sep, run, cam, os.sep)
    if not os.path.exists(base):
        dta = vhub_links[run][cam]
        try:
            fmt = dta['format']
        except KeyError:
            dta = dta['bare']
            fmt = dta['format']
        if fmt == "video_mp4":
            if not os.path.exists(base + ".mp4"):
                download_dataset(run=run, cam=cam)
            convert_video_to_imgseq(_videoname(run, cam), base)
        elif fmt == "zip-archive":
            unarchive_imgseq(src=download_dataset(run=run, cam=cam), base=base)
        else:
            raise ValueError("Got an unknown format '%s' for run '%s', "
                             "cam '%s'" % (fmt, run, cam))
    lbl = ""
    for f in os.listdir(base):
        lbl = f[f.rfind('.') + 1:]
        if lbl in img_format_labels:
            break
    if lbl not in img_format_labels:
        raise ImageFormatError(
            "Did not find any valid image files in %s.\n"
            "Valid image types are: %s" % (base, img_format_labels))
    if not show_warnings:
        warnings.simplefilter("ignore", UserWarning)
    ret = pims.ImageSequence(base + "*." + lbl, as_grey=True, dtype=numpy.float)
    return ret


runs = [
    'pr06', 'pr05', 'ir16', 'ir15', 'ir14', 'ir13', 'ir12', 'ir07', 'ir06',
    'ir05', 'ir04', 'ir03', 'tx02'
]


vhub_links = {
    'pr06': {
        'dataset': 'https://vhub.org/resources/4211',
        'casio-f1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4212/download/2017-09-26'
                       '_pressure-run06_casio-f1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4213/download/2017-09-26'
                       '_pressure-run06_casio-f1_injection_overlay_p30.mp4'
            }
        },
        'rx100v': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4222/download/2017-09-26'
                       '_pressure-run06_sony-rx100v_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4223/download/2017-09-26'
                       '_pressure-run06_sony-rx100v_injection_overlay_p30.mp4'
            }
        },
        'pco': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4216/download/2017-09-26'
                       '_pressure-run06_pco_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4217/download/2017-09-26'
                       '_pressure-run06_pco_injection_overlay_p30.mp4'
            }
        }
    },
    'pr05': {
        'dataset': 'https://vhub.org/resources/4237',
        'sony-4k2': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4238/download/2017-09-13'
                   '_pressure-run05_sony-4k2_injection.mp4'
        }
    },
    'ir16': {
        'dataset': 'https://vhub.org/resources/4240',
        'casio-f1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4241/download/2017-01-21'
                       '_injection-run16_casio-f1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4242/download/2017-01-21'
                       '_injection-run16_casio-f1_injection_overlay_p30.mp4'
            }
        },
        'sony-4k1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4243/download/2017-01-21'
                   '_injection-run16_sony-4k1_injection.mp4'
        },
        'sony-4k2': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4244/download/2017-01-21'
                   '_injection-run16_sony-4k2_injection.mp4'
        },
        'sony-cx220': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4245/download/2017-01-21'
                   '_injection-run16_sony-cx220_injection.mp4'
        }
    },
    'ir15': {
        'dataset': 'https://vhub.org/resources/4246',
        'casio-f1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4252/download/2016-11-27'
                       '_injection-run15_casio-f1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4254/download/2016-11-27'
                       '_injection-run15_casio-f1_injection_overlay_p30.mp4'
            }
        },
        'sony-4k1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4253/download/2016-11-27'
                       '_injection-run15_sony-4k1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4255/download/2016-11-27'
                       '_injection-run15_sony-4k1_injection_overlay_p30.mp4'
            }
        },
        'sony-4k2': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4256/download/2016-11-27'
                       '_injection-run15_sony-4k2_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4257/download/2016-11-27'
                       '_injection-run15_sony-4k2_injection_overlay_p30.mp4'
            }
        },
        'sony-cx220': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4258/download/2016-11-27'
                       '_injection-run15_sony-cx220_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4259/download/2016-11-27'
                       '_injection-run15_sony-cx220_injection_overlay_p30.mp4'
            }
        }
    },
    'ir14': {
        'dataset': 'https://vhub.org/resources/4261',
        'casio-f1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4262/download/2016-11-09'
                       '_injection-run14_casio-f1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4263/download/2016-11-09'
                       '_injection-run14_casio-f1_injection_overlay_p30.mp4'
            },
        },
        'sony-4k1': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4264/download/2016-11-09'
                       '_injection-run14_sony-4k1_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4265/download/2016-11-09'
                       '_injection-run14_sony-4k1_injection_overlay_p30.mp4'
            }
        },
        'sony-4k2': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4266/download/2016-11-09'
                       '_injection-run14_sony-4k2_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4267/download/2016-11-09'
                       '_injection-run14_sony-4k2_injection_overlay_p30.mp4'
            },
        },
        'sony-cx220': {
            'bare': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4268/download/2016-11-09'
                       '_injection-run14_sony-cx220_injection.mp4'
            },
            'overlay': {
                'format': 'video_mp4',
                'src': 'https://vhub.org/resources/4269/download/2016-11-09'
                       '_injection-run14_sony-cx220_injection_overlay_p30.mp4'
            }
        },
    },
    'ir13': {
        'dataset': 'https://vhub.org/resources/4270',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4271/download/2016-11-02'
                   '_injection-run13_casio-f1_injection.mp4'
        }
    },
    'ir12': {
        'dataset': 'https://vhub.org/resources/4279',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4281/download/2016-09-21'
                   '_injection-run12_casio-f1_injection.mp4'
        }
    },
    'ir07': {
        'dataset': 'https://vhub.org/resources/4289',
        'sony-4k1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4290/download/2016-08-24'
                      '_injection-run07_sony-4k1_injection.mp4'
        },
        'sony-4k2': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4292/download/2016-08-24'
                   '_injection-run07_sony-4k2_injection.mp4'
        }
    },
    'ir06': {
        'dataset': 'https://vhub.org/resources/4293',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4295/download/2016-08-24'
            '_injection-run06_casio-f1_injection.mp4'
        }
    },
    'ir05': {
        'dataset': 'https://vhub.org/resources/4299',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4300/download/2016-08-12'
                   '_injection-run05_casio-f1_injection.mp4'
        }
    },
    'ir04': {
        'dataset': 'https://vhub.org/resources/4306',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4308/download/2016-08-12'
                   '_injection-run04_casio-f1_injection.mp4'
        }
    },
    'ir03': {
        'dataset': 'https://vhub.org/resources/4313',
        'casio-f1': {
            'format': 'video_mp4',
            'src': 'https://vhub.org/resources/4315/download/2016-08-10'
                   '_injection-run03_casio-f1_injection.mp4'
        }
    },
    'tx02': {
        'dataset': 'https://vhub.org/resources/4340',
        'nac': {
            'format': 'zip-archive',
            'src': ['https://vhub.org/resources/4344/download/tx02_nac-0.zip',
                    'https://vhub.org/resources/4345/download/tx02_nac-1.zip']
        }
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
    'ir03': {'casio-f1': ''},
    'tx02': {'nac': []}
}
for k in runs:
    itm = tested_videos[k]
    for kk in itm.keys():
        try:
            sitm = vhub_links[k][kk]
            if 'src' in sitm.keys():
                tested_videos[k][kk] = sitm['src']
            elif 'bare' in sitm.keys():
                tested_videos[k][kk] = sitm['bare']['src']
            else:
                raise KeyError("Wrong format in %s" % sitm)
        except:
            print(k, kk)
            raise
