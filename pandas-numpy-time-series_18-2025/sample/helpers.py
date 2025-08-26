import numpy
import pandas


def np_growth(values: pandas.Series) -> numpy.ndarray:
    """Compute percentage growth between consecutive values."""
    arr = values.to_numpy(dtype=float)
    out = numpy.empty_like(arr, dtype=float)
    out[:] = numpy.nan

    prev = arr[:-1]
    curr = arr[1:]

    with numpy.errstate(invalid="ignore", divide="ignore"):
        res = (curr - prev) / prev * 100.0
    res[numpy.isclose(prev, 0.0)] = numpy.nan

    out[1:] = res
    return out


def moving_average_nan(series: pandas.Series, window: int = 3) -> numpy.ndarray:
    """Compute moving average, ignoring NaNs."""
    x = series.to_numpy(dtype=float)
    mask = ~numpy.isnan(x)
    x_filled = numpy.where(mask, x, 0.0)
    k = numpy.ones(window, dtype=float)

    num = numpy.convolve(x_filled, k, mode="same")
    den = numpy.convolve(mask.astype(float), k, mode="same")

    return numpy.divide(num, den, out=numpy.full_like(num, numpy.nan), where=den > 0)


def zscore_nan(series: pandas.Series) -> numpy.ndarray:
    """Compute z-score, ignoring NaNs."""
    x = series.to_numpy(dtype=float)
    mu = numpy.nanmean(x)
    sd = numpy.nanstd(x)

    if not numpy.isfinite(sd) or numpy.isclose(sd, 0.0):
        return numpy.full_like(x, numpy.nan)

    return (x - mu) / sd
