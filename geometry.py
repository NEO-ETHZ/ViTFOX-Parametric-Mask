import gdstk

def rectangle(x: float, y: float, origin: tuple[float, float] = (0,0)) -> gdstk.Polygon:
    """Returns a rectangular polygon centred around origin of shape (x, y).

    Parameters
    ----------
    x : float
        The horizontal size of the octagon.
    y : float, optional
        The vertical size of the octagon. Defaults to x.
    origin: (float, float), optional
        The coordinate around which to centre the octagon. Defaults to (0, 0).
    Returns
    -------
    gdstk.Polygon
        A polygon with the points of an rectangle.
    """
    return gdstk.rectangle(
        (origin[0]-x/2, origin[1]-y/2), 
        (origin[0]+x/2, origin[1]+y/2)
    )

def octagon(x: float, y: float | None = None, origin: tuple[float, float] = (0,0), ratio_x: float = 1/6, ratio_y: float | None = None) -> gdstk.Polygon:
    """Returns an octagon polygon centred around origin of shape (x, y).

    Parameters
    ----------
    x : float
        The horizontal size of the octagon.
    y : float, optional
        The vertical size of the octagon. Defaults to x.
    origin: (float, float), optional
        The coordinate around which to centre the octagon. Defaults to (0, 0).
    ratio_x : float, optional
        How far to cut the corners of a rectangle back in x to form the
        octagonal shape. Defaults to 1/6.
    ratio_y : float, optional
        How far to cut the corners of a rectangle back in y to form the
        octagonal shape. Defaults to 1/6.
    
    Returns
    -------
    gdstk.Polygon
        A polygon with the points of an octagon.
    """
    if y is None:
        y = x
    if ratio_y is None:
        ratio_y = ratio_x
    return gdstk.Polygon([
            (origin[0]+2*x*ratio_x, origin[1]+y/2),
            (origin[0]+x/2,         origin[1]+2*y*ratio_y),
            (origin[0]+x/2,         origin[1]-2*y*ratio_y),
            (origin[0]+2*x*ratio_x, origin[1]-y/2),
            (origin[0]-2*x*ratio_x, origin[1]-y/2),
            (origin[0]-x/2,         origin[1]-2*y*ratio_y),
            (origin[0]-x/2,         origin[1]+2*y*ratio_y),
            (origin[0]-2*x*ratio_x, origin[1]+y/2)
        ])


def route_90deg(c0: tuple[float, float], c1: tuple[float, float], method: str="-|") -> list[tuple[float, float]]:
    """Returns three points connecting two coordinates with a right angle path.
    
    Parameters
    ----------
    c0 : (float, float)
        Coordinate of the first point.
    c1 : (float, float)
        Coordinate of the second point.
    method : str, optional
        Whether to go vertical or horizontal first. Defaults to '-|'.
    
    Returns
    -------
    list of (float, float)
        A list of the original coordinates with the corner coordinate inserted
        between them.
    
    Raises
    ------
    ValueError
        If the method is not '-|' or '|-'.
    """
    match method:
        case "-|":
            corner = (c1[0], c0[1])
        case "|-":
            corner = (c0[0], c1[1])
        case _:
            raise ValueError(f"Unknown routing method '{method}'.")
    return [c0, corner, c1]


def set_layer_datatype(polygon: gdstk.Polygon, layer_datatype: tuple[int, int]) -> None:
    """Sets the layer and datatype tuple for the polygon.
    
    Parameters
    ----------
    polygon: gdstk.Polygon
        The polygon of which to set layer and datatype.
    layer_datatype: (int, int)
        The layer and datatype to set the polygon to
    """
    polygon.layer = layer_datatype[0]
    polygon.datatype = layer_datatype[1]


def convert_to_boundary(polygon: gdstk.Polygon, width: float) -> list[gdstk.Polygon]:
    """Creates polygons that form a boundary of supplied width extending out
    from the supplied polygon.
    
    Parameters
    ----------
    polygon: gdstk.Polygon
        The polygon to operate on.
    width: float
        The size of the boundary.
    
    Returns
    -------
    list of gdstk.Polygon
        A list containg the polygons defining the boundary of the input polygon.
    """
    enlarged = gdstk.offset(polygon, width)
    return gdstk.boolean(enlarged, polygon, "not", layer=polygon.layer, datatype=polygon.datatype)


def reverse_polarity(polygon: gdstk.Polygon, bounding_polygon: gdstk.Polygon) -> list[gdstk.Polygon]:
    """Subtracts the first polygon from the second polygon.
    
    Parameters
    ----------
    polygon: gdstk.Polygon
        The polygon to subtract.
    bounding_polygon: gdstk.Polygon
        The polygon to be subtracted from.
    
    Returns
    -------
    list of gdstk.Polygon
        A list containg the polygons resulting from the subtraction.
    """
    return gdstk.boolean(bounding_polygon, polygon, "not", layer=polygon.layer, datatype=polygon.datatype)


def flatten(input: list) -> list:
    """Flattens the supplied list recursively.
    
    Parameters
    ----------
    input : float
        The possibly nested list to flatten.
    
    Returns
    -------
    list
        A list of all entries of the input
    """
    result = []
    for item in input:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
