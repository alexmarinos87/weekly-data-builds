import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy
import pandas
from sample.helpers import np_growth, moving_average_nan, zscore_nan


def test_np_growth_normal():
    s = pandas.Series([100, 110, 121])
    result = np_growth(s)
    expected = numpy.array([numpy.nan, 10.0, 10.0])
    numpy.testing.assert_allclose(result, expected, rtol=1e-5, equal_nan=True)


def test_np_growth_near_zero():
    s = pandas.Series([0.001, 1000.0])
    result = np_growth(s)
    assert numpy.isnan(result[0])
    assert result[1] > 1e6 or numpy.isnan(result[1])


def test_moving_average_with_nans():
    s = pandas.Series([1.0, numpy.nan, 2.0])
    result = moving_average_nan(s, window=3)
    # Should return moving average ignoring NaN
    # Example: [1.0, 1.5, 2.0]
    expected = numpy.array([1.0, 1.5, 2.0])
    numpy.testing.assert_allclose(result, expected, rtol=1e-5, equal_nan=True)


def test_zscore_nan_behavior():
    s = pandas.Series([1.0, 2.0, 3.0, numpy.nan])
    result = zscore_nan(s)
    assert numpy.isnan(result[3])  # last value should stay NaN
    assert numpy.isclose(numpy.nanmean(result), 0.0, atol=1e-5)  # mean ~ 0
