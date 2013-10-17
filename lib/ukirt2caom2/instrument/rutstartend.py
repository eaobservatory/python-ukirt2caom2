from datetime import datetime, time

from jcmt2caom2.mjd import utc2mjd

from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_temporal_wcs import TemporalWCS

def rut_start_end(date, headers):
    time_start = headers[0].get('RUTSTART')
    time_end = headers[0].get('RUTEND')

    if not (isinstance(time_start, float) and
            isinstance(time_end, float)):
        return None

    date_start = datetime.combine(date.date(), float_to_time(time_start))
    date_end = datetime.combine(date.date(), float_to_time(time_end))

    time = CoordAxis1D(Axis('TIME', 'd'))
    time.range = CoordRange1D(
            RefCoord(0.5, utc2mjd(date_start)),
            RefCoord(1.5, utc2mjd(date_end)))

    return TemporalWCS(time, 'UTC')

def float_to_time(time_float):
    hours = int(time_float)
    time_float = 60 * (time_float - hours)
    minutes = int(time_float)
    time_float = 60 * (time_float - minutes)
    seconds = int(time_float)

    return time(hours, minutes, seconds)


