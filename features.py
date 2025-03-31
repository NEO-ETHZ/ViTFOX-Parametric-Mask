import gdstk

import config

import geometry as geom


def um_to_str(um: float) -> int:
    """Converts the float representing microns to nanometres for string output
    """
    return int(um*1e3)


def make_lower_pad(size_x: float, size_y: float | None=None, tol: float = 30, via: bool = True) -> gdstk.Cell:
    """
    """
    if size_y is None:
        size_y = size_x
    pad = gdstk.Cell(f"LowerPad_{um_to_str(size_x)}_{size_y}")
    # pad at bottom, technically not required I guess
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
    """
    """
    if size_y is None:
        size_y = size_x
    if min(size_x, size_y)  < tol:
        raise ValueError("Pad size too small.")
    pad = gdstk.Cell("UpperPad")
    # pad at bottom, technically not required
    pad_metal = geom.octagon(size_x, size_y)
    geom.set_layer_datatype(pad_metal, config.layers["W2"])
    pad.add(pad_metal)
    return pad


def make_wire(points: list[tuple[float, float]], width: float, level: str) -> gdstk.FlexPath:
    """
    """
    return gdstk.FlexPath(points, width, layer=config.layers[level][0], datatype=config.layers[level][1])


def make_ferro_device(mesa_size: float, via_size: float = config.UVL, device_extent: tuple[float, float] = (40, 20), short: bool=False) -> tuple[gdstk.Cell, tuple[float, float], tuple[float, float]]:
    """
    """
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
    
    top_connection = (-device_extent[0]/4, 0)
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
    via_centre = (device_extent[0]/4, 0)
    bottom_connection = via_centre # or couldd shift (device_extent[0]/2, 0)
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
    N = mesa_m1.bounding_box()[1][1] + config.UVL
    W = mesa_m0.bounding_box()[0][0] - config.UVL
    S = mesa_m1.bounding_box()[0][1] - config.UVL
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