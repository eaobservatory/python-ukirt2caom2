from caom2.wcs.caom2_coord2d import Coord2D
from caom2.wcs.caom2_ref_coord import RefCoord

def to_coord2D(coord, xpix=1.0, ypix=1.0):
    (ra, dec) = coord.deg()

    return Coord2D(RefCoord(float(xpix), ra),
                   RefCoord(float(ypix), dec))


