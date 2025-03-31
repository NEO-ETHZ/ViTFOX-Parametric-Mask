import gdstk
import numpy as np

def rectangle(x: float, y: float, origin: tuple[float, float] = (0,0)) -> gdstk.Polygon:
    """Returns a rectangular polygon centred around origin of shape (x, y).
    """
    return gdstk.rectangle(
        (origin[0]-x/2, origin[1]-y/2), 
        (origin[0]+x/2, origin[1]+y/2)
    )

def octagon(x: float, y: float | None = None, origin: tuple[float, float] = (0,0), ratio_x: float = 1/6, ratio_y: float | None = None) -> gdstk.Polygon:
    """Returns an octagon polygon centred around origin of shape (x, y).
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

def route_90deg(c0: tuple[float, float], c1: tuple[float, float], method="-|") -> list[tuple[float, float]]:
    """Returns three points connecting two coordinates with a right angle path.
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
    """
    polygon.layer = layer_datatype[0]
    polygon.datatype = layer_datatype[1]

def convert_to_boundary(polygon: gdstk.Polygon, width: float) -> list[gdstk.Polygon]:
    """Creates polygons that form a boundary of supplied width extending out from the supplied polygon.
    """
    enlarged = gdstk.offset(polygon, width)
    return gdstk.boolean(enlarged, polygon, "not", layer=polygon.layer, datatype=polygon.datatype)

def reverse_polarity(polygon: gdstk.Polygon, bounding_polygon: gdstk.Polygon) -> list[gdstk.Polygon]:
    """Subtracts the first polygon from the second polygon.
    """
    return gdstk.boolean(bounding_polygon, polygon, "not", layer=polygon.layer, datatype=polygon.datatype)

def flatten(input: list):
    """Flattens the supplied list recursively.
    """
    result = []
    for item in input:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def make_label(text: str, size: float=40, origin: tuple[float, float]=(0, 0), vertical: bool=False, layer: int=0, datatype: int=0) -> list[gdstk.Polygon]:
    """Create text label and centre at (0, 0).

    Size is roughly height in um for capitalised characters.
    """
    ratio = 11/16 # may depend on font
    text = gdstk.text(text, size*ratio, (0, 0), vertical=vertical, layer=layer, datatype=datatype)
    # centre text w.r.t. to bounding box, so anchor is there not bottom left
    if len(text) != 0:
        ((x0, y0), (x1, y1)) = text[0].bounding_box()
        bbox = [[x0, y0], [x1, y1]]
        for polygon in text:
            polygon_bbox = polygon.bounding_box()
            if bbox[0][0] > polygon_bbox[0][0]:
                bbox[0][0] = polygon_bbox[0][0]
            if bbox[0][1] > polygon_bbox[0][1]:
                bbox[0][1] = polygon_bbox[0][1]
            if bbox[1][0] < polygon_bbox[1][0]:
                bbox[1][0] = polygon_bbox[1][0]
            if bbox[1][1] < polygon_bbox[1][1]:
                bbox[1][1] = polygon_bbox[1][1]
        # translate text
        for polygon in text:
            polygon.translate(*(-1 * np.mean(bbox, axis=0)))
            polygon.translate(origin)
    return text

