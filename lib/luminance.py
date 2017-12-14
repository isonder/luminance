import numpy as _np
from numpy import ndarray as _nda
from slicerator import Slicerator as _Slicerator
import multiprocessing as _mp
from scipy.interpolate import UnivariateSpline as _UnvS
import scipy.signal as _sig
from mopics import ImageIndex

_nprocs = _mp.cpu_count()
_iidx = None


def cumul_bright(frame: _nda, select: tuple=None) -> float:
    """Computes the cumulative, relative luminance of an image
    :param frame: Image to compute the luminance from.
    :param select: ((start0, end0), (start1, end1)). Optional, to select subset
      of `frame`.
    :return: L
    """
    if select is None:
        start0, start1 = 0, 0
        end0, end1 = frame.shape
    else:
        ((start0, end0), (start1, end1)) = select
    return frame[start0:end0, start1:end1].sum()


def luminance(frame: _nda, fov: float, ref: float, noise: float,
              select: tuple=None):
    """

    :param frame:
    :param fov: Field of view (m^2).
    :param ref:
    :param noise:
    :param select:
    :return:
    """
    return fov * (cumul_bright(frame, select) - noise) / (ref - noise)


def _cbright_chunk(chunk: _Slicerator,
                   select: tuple, start: int, end: int, que: _mp.Queue):
    """"""
    act = _np.empty(len(chunk), dtype=_np.float)
    for i, frame in enumerate(chunk):
        act[i] = cumul_bright(frame, select)
    que.put((act, start, end))


def cumul_bright_sequence(seq: _Slicerator,
                          select: tuple=None, processes: int=_nprocs) -> _nda:
    """Compute the luminance of each frame in `seq` using the `luminance()`
      function. Arguments other than `seq` and `processes are passed unmodified
      to `cumul_brightness()`.

    :param seq: Image sequence to compute the luminance from.
    :param select: ((start0, end0), (start1, end1)). Optional, to select subset
      of a frame in `seq`.
    :param processes: Number of system processes to use. Default is number of
      system CPUs.
    :return: L(t)
    """
    itms_per_proc, rem = len(seq) // processes, len(seq) % processes
    que = _mp.Queue()
    start, end, procs, idx = 0, -1, [], []
    for k in range(processes):
        end = start + itms_per_proc
        p = _mp.Process(
            target=_cbright_chunk,
            args=(seq[start:end], select, start, end, que))
        procs.append(p)
        start = end
        p.start()
    p = _mp.Process(
        target=_cbright_chunk,
        args=(seq[start:], select, start, len(seq), que))
    procs.append(p)
    p.start()
    act = _np.empty(len(seq), dtype=_np.float)
    for _ in range(len(procs)):
        chunk, start, end = que.get()
        try:
            act[start:end] = chunk
        except ValueError:
            print("chunk:", chunk)
            print("start:", start, "end:", end)
            raise
    for p in procs:
        p.join()
    return act


def average_cbright(chunk: _Slicerator, select: tuple=None,
                    uncert: bool=False, nprocs: int=_nprocs):
    """Convenience method to compute the average cumulative brightness of given
     image sequence selection. Useful to determine the noise level.

    :param chunk: Image sequence/chunk.
    :param select: Selection of images to work on.
    :param uncert: Whether to return standard deviation alongside average value.
    :param nprocs: Number of processes to use.
    :return: Averaged brightness.
    """
    ret = cumul_bright_sequence(chunk, select, nprocs)
    if uncert:
        return ret.mean(), ret.std()
    else:
        return ret.mean()


def luminance_sequence(seq: _Slicerator, fov: float, ref: float, noise: float,
                       select: tuple=None, processes: int=_nprocs) -> _nda:
    """

    :param seq: Image sequence, or part of image sequence.
    :param fov: Camera's field of view (typically in square meters).
    :param ref: Reference brightness (melt brightness) to normalize.
    :param noise: Noise (brightness) level. Typically computed by calling
     `average_cbright()` with a suitable selection of the main sequence.
    :param select: Optional selection of images.
    :param processes: Number of processes to use (default is number of host
     CPUs).
    :return: Luminance (in square meters) for each frame in given input
     sequence.
    """
    return fov * (cumul_bright_sequence(seq, select, processes) - noise) \
        / (ref - noise)


def sigma_luminance(lum, ref: float, sref: float, noise: float, snoise: float,
                    fov: float, sfov:float):
    """Standard deviation of luminance.

    :param lum: Luminance (float or ndarray).
    :param ref: Reference (melt) brightness.
    :param sref: Standard deviation of `ref`.
    :param noise: Background noise brightness (B0).
    :param snoise: Standard deviation of `noise`.
    :param fov: Camera's or frame's field of view.
    :param sfov: Standard deviation of `fov`
    :return:
    """
    return _np.sqrt(
        (lum / (ref - noise)) ** 2 * sref ** 2
        + (-fov / (ref - noise) + lum / (ref - noise)) ** 2 * snoise ** 2
        + (lum / fov) ** 2 * sfov ** 2
    )


def sigma_ldot(ldot, lum, slum, srate, ssrate, lmin: float=1e-4) -> _nda:
    """Standard deviation of Ldot (time derivative of luminance).

    :param ldot:
    :param lum:
    :param slum:
    :param srate:
    :param ssrate:
    :param lmin:
    :return:
    """
    if isinstance(ldot, _nda):
        idx = lum >= lmin
        ret = _np.nan * _np.empty_like(ldot)
        ret[idx] = _np.sqrt(
            (ldot[idx] * slum[idx] / lum[idx]) ** 2
            + (ssrate / srate * ldot[idx]) ** 2
        )
        return ret
    else:
        if lum < lmin:
            return _np.nan
        else:
            return _np.sqrt((ldot * slum / lum) ** 2
                            + (ldot * ssrate / srate) ** 2)


def dldot(t: _nda, lum: _UnvS, threshold: float=None, invalid: float=_np.nan):
    """Speed associated with luminance. Returns v = dot(L) / (2 sqrt(L)).

    :param t: Time array.
    :param lum: Luminance spline. This has to be a spline, since the smoothing
      should be done manually.
    :param threshold: Noise threshold value. At luminosities below this value
      `dldot` will return the value passed to `invalid`.
    :param invalid:
    :return:
    """
    lumn = lum(t)
    ret = _np.empty_like(lumn)
    if threshold is not None:
        idx = lumn < threshold
        ret[idx] = invalid
        idx = _np.logical_not(idx)
        ret[idx] = lum.derivative(n=1)(t[idx]) / (2 * _np.sqrt(lumn[idx]))
    else:
        ret = lum.derivative(n=1)(t) / (2 * _np.sqrt(lumn))
    return ret


def centroid(frame: _nda, ref_bright: float, select: tuple=None) -> _nda:
    if select is None:
        start0, start1 = 0, 0
        end0, end1 = frame.shape
    else:
        ((start0, end0), (start1, end1)) = select
    fr = _np.asarray(frame[start0:end0, start1:end1])
    global _iidx
    if not isinstance(_iidx, ImageIndex):
        _iidx = ImageIndex()
    idx = _iidx(fr.shape)
    return _np.sum((fr[idx[:, 0], idx[:, 1]] / ref_bright) * idx.T, axis=1)


def _centroid_chunk_sequence(
        chunk: _Slicerator, ref_bright: float, select: tuple,
        start: int, end: int, que: _mp.Queue):
    ret = _np.empty((len(chunk), 2), dtype=_np.float)
    for i, frame in enumerate(chunk):
        ret[i] = centroid(frame, ref_bright, select)
    que.put((ret, start, end))


def centroid_sequence(seq: _Slicerator, ref_bright: float,
                      select: tuple=None, processes: int=_nprocs) -> _nda:
    """
    """
    itms_per_proc, rem = len(seq) // processes, len(seq) % processes
    que = _mp.Queue()
    start, end, procs, idx = 0, -1, [], []
    for k in range(processes):
        end = start + itms_per_proc
        p = _mp.Process(
            target=_centroid_chunk_sequence,
            args=(seq[start:end], ref_bright, select, start, end, que))
        procs.append(p)
        start = end
        p.start()
    p = _mp.Process(
        target=_cbright_chunk,
        args=(seq[start:], select, start, len(seq), que))
    procs.append(p)
    p.start()
    cent = _np.empty((len(seq), 2), dtype=_np.float)
    for _ in range(len(procs)):
        chunk, start, end = que.get()
        try:
            cent[start:end] = chunk
        except ValueError:
            print("chunk:", chunk)
            print("start:", start, "end:", end)
            raise
    for p in procs:
        p.join()
    return cent


class FilterProfile:
    def __init__(self, cname: str, srate: float, filterfreq: _nda,
                 filterwidth: float=1.5):
        self.cname = cname
        self.srate = srate
        self.freqs = filterfreq
        self.filterwidth = filterwidth


prof_casiof1 = FilterProfile(
    'Casio F1', srate=300.,
    filterfreq=_np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140])
)


def filter_lum(lum: _nda, profile: FilterProfile):
    fw = profile.filterwidth
    r = profile.srate
    pars = [
        _sig.bessel(
            2, _np.array([fr - fw, fr + fw]) / (0.5 * r),
            btype='bandstop', analog=False)
        for fr in profile.freqs
    ]
    filtered = lum.copy()
    for bb, ab in pars:
        filtered = _sig.filtfilt(bb, ab, filtered, axis=0)
    return filtered