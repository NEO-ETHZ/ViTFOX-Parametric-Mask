import gdstk

import config

import geometry as geom
import features as feat

lower_pad = feat.make_lower_pad(config.pad_dim)


def FED2T(name: str, mesa_size: float, via_size: float=config.UVL, short: bool=False) -> gdstk.Cell:
    """Generate a cell containg a two terminal ferroelectric resistive devices.
    
    Parameters
    ----------
    name : string
        The text to write above the device for identification.
    mesa_size : float
        The size of the mesa.
    via_size : float, optional
        The size of the via, by default the UVL clearance.
    short : bool, optional
        Whether the electrodes should be shorted, bypassing the ferroelectric.
        Defaults to False.
    
    Returns
    -------
    gdstk.Cell
        The cell containing the device components.
    """
    Device, lower, upper = feat.make_ferro_device(mesa_size, via_size, short=short)
    Main = gdstk.Cell(f"2T_M{mesa_size}_V{via_size}")
    # device
    D = gdstk.Reference(Device, (0,0))
    # pads
    UP = gdstk.Reference(lower_pad, (D.origin[0] + upper[0] - config.pad_device_spacing - config.pad_dim/2, D.origin[1] + upper[1]))
    LP = gdstk.Reference(lower_pad, (D.origin[0] + lower[0] + config.pad_device_spacing + config.pad_dim/2, D.origin[1] + lower[1]))
    # wires
    wire_LP_D = feat.make_wire(
        geom.route_90deg((D.origin[0] + lower[0], D.origin[1] + lower[1] + config.wire_width/2), LP.origin, "|-"),
        config.wire_width, "W1")
    wire_UP_D = feat.make_wire(
        geom.route_90deg((D.origin[0] + upper[0], D.origin[1] + upper[1]), UP.origin),
        config.wire_width, "W1")
    # stick together
    _ = Main.add(UP, LP, wire_LP_D, wire_UP_D, D)
    # label
    label = feat.make_label(name, origin=(0, D.origin[1] - config.pad_device_spacing - config.pad_dim/2), layer=config.layers["label"][0], datatype=config.layers["label"][1])
    _ = Main.add(*label)
    return Main


def make_vector_1xN(name: str, mesa_sizes: list[float], via_size: float=config.UVL) -> gdstk.Cell:
    """Generate a cell containg a vector of two terminal ferroelectric resistive
    devices. The bottom electrodes of these devices are electrically connected.
    
    Parameters
    ----------
    name : string
        The text to write above the device for identification.
    mesa_size : list of floats
        The sizes of the mesas in the vector, determines the length of the vector.
    via_size : float, optional
        The size of the vias, by default the UVL clearance.
    
    Returns
    -------
    gdstk.Cell
        The cell containing the vector components.
    """
    N = len(mesa_sizes)
    Main = gdstk.Cell(f"Vector{N}_M{str(mesa_sizes).replace(', ', '_')[1:-1]}_V{via_size}")
    y_step = config.pad_dim + config.pad_dim/4
    for i, mesa_size in enumerate(mesa_sizes):
        Device, lower, upper = feat.make_ferro_device(mesa_size, via_size)
        D = gdstk.Reference(Device, (0, i*y_step))
        UP = gdstk.Reference(lower_pad, (D.origin[0] + upper[0] - config.pad_device_spacing - config.pad_dim/2, D.origin[1] + upper[1]))
        LP = gdstk.Reference(lower_pad, (D.origin[0] + lower[0] + config.pad_device_spacing + config.pad_dim/2, D.origin[1] + lower[1]))
        wire_UP_D = feat.make_wire(
            geom.route_90deg((D.origin[0] + upper[0], D.origin[1] + upper[1]), UP.origin),
            config.wire_width, "W1")
        wire_LP_D = feat.make_wire(
            geom.route_90deg((D.origin[0] + lower[0], D.origin[1] + lower[1] + config.wire_width/2), LP.origin, "|-"),
            config.wire_width, "W1")
        _ = Main.add(LP, UP, wire_UP_D, wire_LP_D, D)
    # connect all right pads with another
    shared_pad = geom.rectangle(config.pad_dim*2/3, y_step * N - config.pad_dim, origin=(LP.origin[0],config.pad_device_spacing+(y_step*i-config.pad_dim/2)/2))
    geom.set_layer_datatype(shared_pad, config.layers["W1"])
    _ = Main.add(shared_pad)
    # label
    label = feat.make_label(name, origin=(0, - config.pad_device_spacing - config.pad_dim/2), layer=config.layers["label"][0], datatype=config.layers["label"][1])
    _ = Main.add(*label)
    return Main


def make_xbar_2x2(name: str, mesa_sizes: list[list[float, float], list[float, float]], via_size: float=config.UVL)  -> gdstk.Cell:
    """Generate a cell containg a 2x2 cross bar array of two terminal
    ferroelectric resistive devices.
    
    Parameters
    ----------
    name : string
        The text to write above the device for identification.
    mesa_sizes : nested list of floats
        The sizes of the mesas in the cross bar array. Should of shape (2, 2).
    via_size : float, optional
        The size of the vias, by default the UVL clearance.
    
    Returns
    -------
    gdstk.Cell
        The cell containing the cross bar components.
    """
    Main = gdstk.Cell(f"XBAR_M{str(mesa_sizes).replace(', ', '_')[2:-2].replace(']_[', '__')}_V{via_size}")
    sep = config.pad_dim/4
    Device_NW, lower_NW, upper_NW = feat.make_ferro_device(mesa_sizes[0][0], via_size)
    Device_NE, lower_NE, upper_NE = feat.make_ferro_device(mesa_sizes[0][1], via_size)
    Device_SW, lower_SW, upper_SW = feat.make_ferro_device(mesa_sizes[1][0], via_size)
    Device_SE, lower_SE, upper_SE = feat.make_ferro_device(mesa_sizes[1][1], via_size)
    D_NW = gdstk.Reference(Device_NW, ( 0, sep + config.pad_dim))
    D_NE = gdstk.Reference(Device_NE, (sep*2, sep + config.pad_dim))
    D_SW = gdstk.Reference(Device_SW, ( 0, 0))
    D_SE = gdstk.Reference(Device_SE, (sep*2, 0))
    _ = Main.add(D_NW, D_NE, D_SW, D_SE)
    UP_1 = gdstk.Reference(lower_pad, (-sep*1.5 - config.pad_dim/2,  sep + config.pad_dim))
    UP_2 = gdstk.Reference(lower_pad, (sep*1.5 + config.pad_dim,  0))
    LP_1 = gdstk.Reference(lower_pad, (-sep*1.5 - config.pad_dim/2,   0))
    LP_2 = gdstk.Reference(lower_pad, (sep*1.5 + config.pad_dim,  sep + config.pad_dim))
    _ = Main.add(LP_1, LP_2, UP_1, UP_2)
    # UP_1
    temp_point = (D_NW.origin[0] + upper_NW[0], D_NW.origin[1] + upper_NW[1] + config.pad_dim/4)
    wire_UP_NW = feat.make_wire(
            geom.route_90deg((D_NW.origin[0] + upper_NW[0], D_NW.origin[1] + upper_NW[1]), UP_1.origin),
            config.wire_width, "W1")
    wire_UP_NE = feat.make_wire(
            geom.route_90deg((D_NE.origin[0] + upper_NE[0], D_NE.origin[1] + upper_NE[1]), temp_point, "|-") +
            geom.route_90deg(temp_point, UP_1.origin, "|-"),
            config.wire_width, "W1")
    _ = Main.add(wire_UP_NW, wire_UP_NE)
    # UP_2
    temp_point = (D_SE.origin[0] + upper_SE[0], D_SW.origin[1] + upper_SW[1] - config.pad_dim/4)
    wire_UP_SW = feat.make_wire(
            geom.route_90deg((D_SW.origin[0] + upper_SW[0], D_SW.origin[1] + upper_SW[1]), temp_point, "|-"),
            config.wire_width, "W1")
    temp_point2 = (D_SE.origin[0] - 3*upper_SE[0], 0)
    wire_UP_SE = feat.make_wire(
            [(D_SE.origin[0] + upper_SE[0], D_SE.origin[1] + upper_SE[1]), temp_point] +
             geom.route_90deg(temp_point, temp_point2, "-|") + [UP_2.origin],
            config.wire_width, "W1")
    _ = Main.add(wire_UP_SW, wire_UP_SE)
    # LP_1
    temp_point = (D_NW.origin[0] + lower_NW[0], (25 + config.pad_dim)/2)
    wire_LP_NW = feat.make_wire(
            geom.route_90deg((D_NW.origin[0] + lower_NW[0], D_NW.origin[1] + lower_NW[1]), temp_point, "|-"),
            config.wire_width, "W1")
    wire_LP_NE = feat.make_wire(
            geom.route_90deg((D_SW.origin[0] + lower_SW[0], D_SW.origin[1] + lower_SW[1]), temp_point, "|-"),
            config.wire_width, "W1")
    temp_point2 = (D_NW.origin[0] - 25/5*4, LP_1.origin[1])
    wire_LP_pad = feat.make_wire(
            geom.route_90deg(temp_point, temp_point2, "-|") +
            [LP_1.origin],
            config.wire_width, "W1")
    _ = Main.add(wire_LP_NW, wire_LP_NE, wire_LP_pad)
    # LP_2
    wire_LP_2 = feat.make_wire(
            [LP_2.origin,
             (D_NE.origin[0] + lower_NE[0], D_NE.origin[1] + lower_NE[1]),
             (D_SE.origin[0] + lower_SE[0], D_SE.origin[1] + lower_SE[1])],
            config.wire_width, "W1")
    _ = Main.add(wire_LP_2)
    # label
    label = feat.make_label(name, origin=(sep, - config.pad_device_spacing - config.pad_dim/2), layer=config.layers["label"][0], datatype=config.layers["label"][1])
    _ = Main.add(*label)
    return Main

