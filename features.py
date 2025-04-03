import gdstk
import numpy as np

import config

import geometry as geom


def um_to_str(um: float) -> int:
    """Converts the float representing microns to nanometres for string output.
    
    Parameters
    ----------
    um : float
        The um value to convert to nm.
    
    Returns
    -------
    int
        The input multiplied by 1'000.
    """
    return int(um*1e3)


def make_lower_pad(size_x: float, size_y: float | None=None, tol: float = 30, via: bool = True) -> gdstk.Cell:
    """Create a cell defining a contact pad starting on the proce card wafer, 
    with an optional via going to the top wiring layer. The pad shape is an
    octagon.
    
    Parameters
    ----------
    size_x : float
        The horizontal dimension of the pad.
    size_y : float, optional
        The vertical dimension of the pad. Defaults to size_x.
    tol : float, optional
        The minimum size that a feature of the pad can be. Defaults to
        30 (um).
    via : bool, optional
        Whether to add a via through the dielectric. Defaults to True.
    
    Returns
    -------
    gdstk.Cell
        A cell representing a probing pad.
    """
    if size_y is None:
        size_y = size_x
    pad = gdstk.Cell(f"LowerPad_{um_to_str(size_x)}_{size_y}")
    pad_metal_bot = geom.octagon(size_x, size_y)
    geom.set_layer_datatype(pad_metal_bot, config.layers["W1"])
    pad.add(pad_metal_bot)
    if via:
        if min(size_x, size_y) - 4*config.UVL < tol:
            raise ValueError("Pad size too small.")
        # via through bonding interface passivation
        pad_via = geom.octagon(size_x - 2*config.UVL, size_y - 2*config.UVL)
        geom.set_layer_datatype(pad_via, config.layers["V2"])
        pad.add(pad_via)
        # via through other passivation
        pad_via = geom.octagon(size_x - 2*config.UVL, size_y - 2*config.UVL)
        geom.set_layer_datatype(pad_via, config.layers["V4"])
        pad.add(pad_via)
        # pad at top
        pad_metal_top = geom.octagon(size_x, size_y)
        geom.set_layer_datatype(pad_metal_top, config.layers["W2"])
        pad.add(pad_metal_top)
    return pad


def make_upper_pad(size_x: float, size_y: float | None=None, tol: float=30) -> gdstk.Cell:
    """Create a cell defining a contact pad on the top of the finished device.
    The pad shape is an octagon.
    
    Parameters
    ----------
    size_x : float
        The horizontal dimension of the pad.
    size_y : float, optional
        The vertical dimension of the pad. Defaults to size_x.
    tol : float, optional
        The minimum size that a feature of the pad can be. Defaults to
        30 (um).
    
    Returns
    -------
    gdstk.Cell
        A cell representing a probing pad.
    """
    if size_y is None:
        size_y = size_x
    if min(size_x, size_y)  < tol:
        raise ValueError("Pad size too small.")
    pad = gdstk.Cell(f"UpperPad_{um_to_str(size_x)}_{size_y}")
    pad_metal = geom.octagon(size_x, size_y)
    geom.set_layer_datatype(pad_metal, config.layers["W2"])
    pad.add(pad_metal)
    return pad


def make_wire(points: list[tuple[float, float]], width: float, level: str) -> gdstk.FlexPath:
    """Connect a list of points with a polygon of fixed width.
    
    Parameters
    ----------
    points : list of (float, float)
        A list containing the points to connect.
    width : float
        The width of the connecting feature.
    level : string
        The string which is the key of the config.layers entry defining on
        which layer/datatype the result should be placed. 
    
    Returns
    -------
    gdstk.Cell
        A cell representing a probing pad.
    """
    return gdstk.FlexPath(points, width, layer=config.layers[level][0], datatype=config.layers[level][1])


def make_ferro_device(mesa_size: float, via_size: float = config.UVL, device_extent: tuple[float, float] = (60, 40), short: bool=False) -> tuple[gdstk.Cell, tuple[float, float], tuple[float, float]]:
    """Generate a ferroelectric device with top and bottom electrodes and
    ferroelectric layer in between.
    
    Parameters
    ----------
    mesa_size : float
        The size of the mesa.
    via_size : float, optional
        The size of the via, by default the UVL clearance.
    device_extent : (float, float)
        The extent of the device, determining the position of the elements.
        Defaults to (80, 40).
    short : bool, optional
        Whether the electrodes should be shorted, bypassing the ferroelectric.
        Defaults to False.
    
    Returns
    -------
    gdstk.Cell
        A cell representing a ferroelectric resistive stack.
    (float, float)
        The coordinates of the contact point of the bottom electrode.
    (float, float)
        The coordinates of the contact point of the top electrode.
    
    Raises
    ------
    ValueError
        If structure dimensions exceed the device size.
    """
    # clearance both vias to electrodes + their clearances, mesa + its clearance,
    # clearance between edges of device and mesa and vias (right side of inequality)
    if  2*via_size + 8*config.UVL + mesa_size + 2*config.UVL > device_extent[0] - 4*config.UVL:
        raise ValueError("Component dimensions exceed device_extent.")
    device = gdstk.Cell(f"FerroelectricDevice_M{um_to_str(mesa_size)}_V{um_to_str(via_size)}")
    if short:
        device = gdstk.Cell(f"FerroelectricDevice_M{um_to_str(mesa_size)}_V{um_to_str(via_size)}_short")
    # (contact to) top electrode
    mesa_centre = (0, 0)
    # mesa metal
    mesa_m0 = geom.octagon(mesa_size, origin=mesa_centre)
    geom.set_layer_datatype(mesa_m0, config.layers["M0"])
    # via through passivation
    via_passivation = geom.octagon(mesa_size - 2*config.EBL, origin=mesa_centre)
    geom.set_layer_datatype(via_passivation, config.layers["V3"])
    # metal on top of passivation
    mesa_m2 = geom.octagon(mesa_size + 2*config.UVL, origin=mesa_centre)
    geom.set_layer_datatype(mesa_m2, config.layers["M2"])
    device.add(mesa_m0, via_passivation, mesa_m2)
    
    top_connection = (-device_extent[0]/2 + via_size + 4*config.UVL, 0)
    # routing across top
    wire_LP_D = make_wire([top_connection, mesa_centre], config.wire_width, "M2")
    via_m2 = geom.octagon(via_size + 2*config.UVL, origin=top_connection)
    geom.set_layer_datatype(via_m2, config.layers["M2"])
    # via through bonding interface to bottom electrode
    via_etch = geom.octagon(via_size, origin=top_connection)
    geom.set_layer_datatype(via_etch, config.layers["V2"])
    # bottom pad
    via_bot_pad = geom.octagon(via_size + 2*config.UVL, origin=top_connection)
    geom.set_layer_datatype(via_bot_pad, config.layers["W1"])
    # via top passivation
    via_p_bot_pad = geom.octagon(via_size + 2*config.UVL, origin=top_connection)
    geom.set_layer_datatype(via_p_bot_pad, config.layers["V4"])
    device.add(via_bot_pad, via_etch, via_p_bot_pad, wire_LP_D, via_m2)
    
    # contact to bottom electrode
    via_centre = (device_extent[0]/2 - via_size - 4*config.UVL, 0)
    bottom_connection = via_centre
    # via through ferroelectric stack
    via_FE = geom.octagon(via_size + 2*config.UVL, origin=via_centre)
    geom.set_layer_datatype(via_FE, config.layers["V1"])
    # via through bonding interface to bottom electrode
    via_etch = geom.octagon(via_size, origin=via_centre)
    geom.set_layer_datatype(via_etch, config.layers["V2"])
    # via metallisation
    mesa_m1 = geom.octagon(via_size + 4*config.UVL, origin=via_centre)
    geom.set_layer_datatype(mesa_m1, config.layers["M1"])
    # bottom pad
    if bottom_connection != via_centre:
        wire_LP_D = make_wire([bottom_connection, via_centre], config.wire_width, "W1")
    via_bot_pad = geom.octagon(via_size + 2*config.UVL, origin=via_centre)
    geom.set_layer_datatype(via_bot_pad, config.layers["W1"])
    device.add(via_etch, mesa_m1, via_bot_pad, wire_LP_D)
    
    # FE extent
    N = max(mesa_m0.bounding_box()[1][1], mesa_m1.bounding_box()[1][1]) + config.UVL
    W = mesa_m0.bounding_box()[0][0] - config.UVL
    S = min(mesa_m0.bounding_box()[0][1], mesa_m1.bounding_box()[0][1]) - config.UVL
    E = mesa_m1.bounding_box()[1][0] + config.UVL
    FE = gdstk.rectangle((W, S), (E, N))
    FE = gdstk.boolean(FE, via_FE, "not")[0]
    geom.set_layer_datatype(FE, config.layers["V1"])
    device.add(FE)
    
    if short:
        short = FE.copy()
        geom.set_layer_datatype(short, config.layers["M1"])
        device.add(short)
    
    return device, bottom_connection, top_connection


def make_label(text: str, size: float=40, origin: tuple[float, float]=(0, 0), vertical: bool=False, layer: int=0, datatype: int=0) -> list[gdstk.Polygon]:
    """Create text label and centre at (0, 0).
    Size is roughly height in um for capitalised characters.
    
    Parameters
    ----------
    text : string
        The text to convert to polygons.
    size : float, optional
        The heigh in um of a capitalised letter. Defaults to 40.
    origin : (float, float), optional
        The position to centre the polygons around. Defaults to (0, 0).
    vertical : bool, optional
        Whether to write the text vertically. Defaults to False.
    layer : int, optional
        The layer to set for the polgons. Defaults to 0.
    datatype : int, optional
        The datatype to set for the polgons. Defaults to 0.
    
    Returns
    -------
    list of gdstk.Polygon
        A list containg the polygons representing the text supplied.
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
