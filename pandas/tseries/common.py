## datetimelike delegation ##

import numpy as np
from pandas.core.base import PandasDelegate
from pandas.core import common as com
from pandas import Series, DatetimeIndex, PeriodIndex
from pandas import lib, tslib

def is_datetimelike(data):
    """ return a boolean if we can be successfully converted to a datetimelike """
    try:
        maybe_to_datetimelike(data)
        return True
    except (Exception):
        pass
    return False

def maybe_to_datetimelike(data, copy=False):
    """
    return a DelegatedClass of a Series that is datetimelike (e.g. datetime64[ns] dtype or a Series of Periods)
    raise TypeError if this is not possible.

    Parameters
    ----------
    data : Series
    copy : boolean, default False
           copy the input data

    Returns
    -------
    DelegatedClass

    """

    if not isinstance(data, Series):
        raise TypeError("cannot convert an object of type {0} to a datetimelike index".format(type(data)))

    index = data.index
    if issubclass(data.dtype.type, np.datetime64):
        return DatetimeProperties(DatetimeIndex(data, copy=copy), index)
    else:
        if com.is_period_arraylike(data):
            return PeriodProperties(PeriodIndex(data, copy=copy), index)

    raise TypeError("cannot convert an object of type {0} to a datetimelike index".format(type(data)))

class Properties(PandasDelegate):

    def __init__(self, values, index):
        self.values = values
        self.index = index

    def _delegate_property_get(self, name):
        result = getattr(self.values,name)

        # maybe need to upcast (ints)
        if isinstance(result, np.ndarray):
            if com.is_integer_dtype(result):
                result = result.astype('int64')

        # return the result as a Series, which is by definition a copy
        result = Series(result, index=self.index)

        # setting this object will show a SettingWithCopyWarning/Error
        result.is_copy = ("modifications to a property of a datetimelike object are not "
                          "supported and are discarded. Change values on the original.")

        return result

    def _delegate_property_set(self, name, value, *args, **kwargs):
        raise ValueError("modifications to a property of a datetimelike object are not "
                         "supported. Change values on the original.")


class DatetimeProperties(Properties):
    """
    Accessor object for datetimelike properties of the Series values.

    Examples
    --------
    >>> s.dt.hour
    >>> s.dt.second
    >>> s.dt.quarter

    Returns a Series indexed like the original Series.
    Raises TypeError if the Series does not contain datetimelike values.
    """

DatetimeProperties._add_delegate_accessors(delegate=DatetimeIndex,
                                           accessors=DatetimeIndex._datetimelike_ops,
                                           typ='property')

class PeriodProperties(Properties):
    """
    Accessor object for datetimelike properties of the Series values.

    Examples
    --------
    >>> s.dt.hour
    >>> s.dt.second
    >>> s.dt.quarter

    Returns a Series indexed like the original Series.
    Raises TypeError if the Series does not contain datetimelike values.
    """

PeriodProperties._add_delegate_accessors(delegate=PeriodIndex,
                                         accessors=PeriodIndex._datetimelike_ops,
                                         typ='property')
