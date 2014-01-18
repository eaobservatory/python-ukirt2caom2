from caom2.wcs.caom2_value_coord2d import ValueCoord2D

def to_coord2D(coord):
    (ra, dec) = coord.deg()

    return ValueCoord2D(ra, dec)


