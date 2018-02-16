"""All luminance related functions"""
import numpy as _np
from numpy import ndarray as _nda
import multiprocessing as _mp
import scipy.signal as _sig

_nprocs = _mp.cpu_count()


def cumul_bright(frame, select=None):
    """Computes the cumulative, relative luminance of an image.

    :param frame: Image to compute the luminance from.
    :type frame: ndarray
    :param select: ((start0, end0), (start1, end1)). Optional, to select subset
     of `frame`.
    :type select: tuple
    :return: Brightness of frame.
    :rtype: float
    """
    if select is None:
        start0, start1 = 0, 0
        end0, end1 = frame.shape
    else:
        ((start0, end0), (start1, end1)) = select
    return frame[start0:end0, start1:end1].sum()


def luminance(frame, fov, ref, noise, select=None):
    """Computes the luminance from a given video frame.

    :param frame: Image frame to compute the luminance from.
    :type frame: 2D `ndarray`
    :param fov: Field of view (square meters).
    :type fov: `float`
    :param ref: Cumulative reference brightness.
    :type ref: `float`
    :param noise: Cumulative brightness of background noise.
    :type noise: `float`
    :param select: Selection marking the subset of `frame` to compute the
     luminance from.
    :type select: `tuple` or `None`
    :return: luminance of `frame`.
    :rtype: `float`
    """
    return fov * (cumul_bright(frame, select) - noise) / (ref - noise)


def _cbright_chunk(chunk, select, start, end, que):
    """**Do not call this directly.**
     Computes the cumulative brightness for a part of an image sequence. This
     method should is called multiple times from `cumul_bright_sequence()` in
     separate processes.

    :param chunk: Complete or partial image  sequence.
    :type chunk: Slicerator
    :param select: Selection marking the subset of `frame` to compute the
     luminance from.
    :type select: tuple
    :param start: Start position in sequence from which `chunk` was selected.
    :type start: int
    :param end: End position in sequence from which `chunk` was selected.
    :type end: int
    :param que: The queue object that manages the multiple processes.
    :type que: multiprocessing.Queue
    :return: None.
    """
    act = _np.empty(len(chunk), dtype=_np.float)
    for i, frame in enumerate(chunk):
        act[i] = cumul_bright(frame, select)
    que.put((act, start, end))


def cumul_bright_sequence(seq, select=None, processes=_nprocs):
    """Compute the cumulative brightness of each frame in `seq` using the
    `luminance()` function. Arguments other than `seq` and `processes are
    passed unmodified to `cumul_brightness()`.

    :param seq: Image sequence to compute the luminance from.
    :type seq: Slicerator
    :param select: ((start0, end0), (start1, end1)). Optional, to select subset
     of a frame in `seq`.
    :type select: tuple
    :param processes: Number of system processes to use. Default is number of
     system CPUs.
    :type processes: int
    :return: brightness array B(t)
    :rtype: ndarray
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


def average_cbright(chunk, select=None, uncert=False, nprocs=_nprocs):
    """Convenience method to compute the average cumulative brightness of
    given image sequence selection. Useful to determine the noise level.

    :param chunk: Image sequence/chunk.
    :type chunk: Slicerator
    :param select: Selection of images to work on.
    :type select: tuple
    :param uncert: Whether to return standard deviation alongside average value.
    :type uncert: bool
    :param nprocs: Number of processes to use.
    :type nprocs: int
    :return: Averaged brightness.
    :rtype: float
    """
    ret = cumul_bright_sequence(chunk, select, nprocs)
    if uncert:
        return ret.mean(), ret.std()
    else:
        return ret.mean()


def luminance_sequence(seq, fov, ref, noise, select=None, processes=_nprocs):
    """Computes the luminance of frame sequence `seq`.

    :param seq: Image sequence, or part of image sequence.
    :type seq: Slicerator
    :param fov: Camera's field of view (typically in square meters).
    :type fov: float
    :param ref: Reference brightness (melt brightness) to normalize.
    :type ref: float
    :param noise: Noise (brightness) level. Typically computed by calling
     `average_cbright()` with a suitable selection of the main sequence.
    :type noise: float
    :param select: Optional selection of images.
    :type select: tuple
    :param processes: Number of processes to use (default is number of host
     CPUs).
    :type processes: int
    :return: Luminance (in square meters) for each frame in given input
     sequence.
    :rtype: ndarray
    """
    return fov * (cumul_bright_sequence(seq, select, processes) - noise) \
        / (ref - noise)


def sigma_luminance(lum, ref, sref, noise, snoise, fov, sfov):
    """Standard deviation of luminance.

    :param lum: Luminance
    :type lum: float or ndarray.
    :param ref: Reference (melt) brightness.
    :type ref: float
    :param sref: Standard deviation of `ref`.
    :type sref: float
    :param noise: Background noise brightness (B0).
    :type noise: float
    :param snoise: Standard deviation of `noise`.
    :type snoise: float
    :param fov: Camera's or frame's field of view.
    :type fov: float
    :param sfov: Standard deviation of `fov`
    :type sfov: float
    :rtype: ndarray
    """
    return _np.sqrt(
        (lum / (ref - noise)) ** 2 * sref ** 2
        + (-fov / (ref - noise) + lum / (ref - noise)) ** 2 * snoise ** 2
        + (lum / fov) ** 2 * sfov ** 2
    )


def sigma_ldot(ldot, lum, slum, srate, ssrate, lmin=1e-4):
    """Standard deviation of Ldot (time derivative of luminance).

    :param ldot: Luminance time derivative.
    :type ldot: ndarray or float
    :param lum: Luminance.
    :type lum: ndarray or float
    :param slum: Standard deviation of luminance.
    :type slum: ndarray or float
    :param srate: sampling rate.
    :type srate: float
    :param ssrate: standard devition of sampling rate.
    :type ssrate: float
    :param lmin: Minimum value of luminance. if `lum` is smaller than this value
     the return value will be made invalid (nan).
    :type lmin: float
    :rtype: ndarray or float
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


def dldot(t, lum, threshold=None, invalid=_np.nan):
    """Speed associated with luminance. Returns v = dot(L) / (2 sqrt(L)).

    :param t: Time array.
    :type t: ndarray
    :param lum: Luminance spline. This has to be a spline, since the smoothing
     should be done manually.
    :type lum: UnivariateSpline
    :param threshold: Noise threshold value. At luminosities below this value
     `dldot` will return the value passed to `invalid`.
    :type threshold: float
    :param invalid: Number to use to signify an invalid value (NaN)
    :rtype: ndarray
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


def sigma_dldot(ldot, sldot, lum, slum, lmin: float):
    """Standard deviation of dldot.
    All parameters except `lmin` should be given either as ndarray, or as
    float, mixed parameter sets will return an error.

    :param ldot: Time derivative of luminance.
    :type ldot: float or ndarray.
    :param sldot: Standard deviation of `ldot`.
    :type sldot: float or ndarray.
    :param lum: Luminance.
    :type lum: float or ndarray.
    :param slum: Uncertainty of `lum`.
    :type slum: float or ndarray.
    :param lmin: Minimum luminance for which to compute `sigma_dldot`.
    :return: 1-sigma uncertainty of dldot.
    :rtype: float or ndarray
    """
    if isinstance(ldot, _nda):
        ret = _np.nan * _np.empty_like(ldot)
        idx = lum > lmin
        ret[idx] = _np.sqrt(
            (sldot[idx] / (2 * lum[idx] ** 0.5)) ** 2 +
            (ldot[idx] * slum[idx] / (4 * lum[idx] ** 1.5)) ** 2
        )
    else:
        assert not isinstance(lum, _nda), \
            "if ldot is given as float, lum must be, too."
        if lum < lmin:
            ret = _np.nan
        else:
            ret = _np.sqrt(
                (sldot / (2 * lum ** 0.5)) ** 2 +
                (ldot * slum / (4 * lum ** 1.5)) ** 2
            )
    return ret


class FilterProfile:
    """A little profile object to store camera specific filter profiles.

    .. attribute:: cname

        A camera identifier.

    .. attribute srate

        Camera's sampling rate.

    .. attribute filterfreq

        Array of frequencies that should be damped from signal.

    .. attribute filterwidth

        Frequency width of the sink in the filter response around each value
        in `filterfreq`.
    """
    def __init__(self, cname, srate, filterfreq, filterwidth=1.5):
        """See above.

        :param cname:
        :param srate:
        :param filterfreq:
        :param filterwidth:
        """
        self.cname = cname
        self.srate = srate
        self.freqs = filterfreq
        self.filterwidth = filterwidth


prof_casiof1 = FilterProfile(
    'Casio F1', srate=300.,
    filterfreq=_np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140])
)


def filter_lum(lum, profile):
    """Filters a luminance (or any other) signal according to the given filter
    profile.

    :param lum: 'raw' signal to be filtered.
    :type lum: ndarray
    :param profile: Filter profile.
    :type profile: FilterProfile
    :return: Filtered signal.
    :rtype: ndarray
    """
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
