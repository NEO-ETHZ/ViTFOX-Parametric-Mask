import gdstk
from datetime import datetime
import numpy as np

import config

import geometry as geom
import components as comp


# define layer mapping
# fill / boundary denotes whether the geometric feature should be kept as a
# polygon or if the boundary should be the result
config.layers = {
    "M0": ( 0, 0, "fill"),      # metallisation top eletrode of FE / STO etch
    "M1": ( 1, 0, "fill"),      # metallisation to bottom electrode of FE
    "M2": (11, 0, "boundary"),  # metallisation from M0 to W2 (set same as top wiring)
    "W1": (10, 0, "boundary"),  # lower layer of wiring
    "W2": (11, 0, "boundary"),  # upper layer of wiring
    "V1": (21, 0, "fill"),      # via through FE
    "V2": (22, 0, "fill"),      # via through bonding interface, M1 to W1
    "V3": (23, 0, "fill"),      # via through passivation, M2 to M0
    "V4": (24, 0, "fill"),      # via through passivation, M2/W2 to W1
    "label": (50, 0, "fill"),   # label in separate layer for convenience
}
# clearances
config.UVL = 2
config.EBL = 0.05

# general design parameter
config.wire_width = 3
config.boundary_width = 1

config.pad_dim = 100

# define location to save mask
#outfile = f"mask_{datetime.now().strftime('%Y%m%d-%H%M%S')}.gds"
outfile = "mask.gds"

# example placement of structures
dev0 = comp.FED2T("FE", 20)
dev1 = comp.make_vector_1xN("VECTOR", np.ones(25)*5)
dev2 = comp.make_xbar_2x2("XBAR", [[1, 2], [3, 4]])
short0 = comp.FED2T("SHORT", 1, short=True)

top = gdstk.Cell("TOP")
top.add(gdstk.Reference(dev0, (0, 0)))
top.add(gdstk.Reference(dev1, (300, 0)))
top.add(gdstk.Reference(dev2, (600, 0)))
top.add(gdstk.Reference(short0, (950, 0)))


# place to library
lib = gdstk.Library()

def add_children(cell: gdstk.Cell, lib: gdstk.Library) -> None:
    """Helper function to automate adding referenced cells to the library.
    """
    _ = lib.add(cell)
    for ref in cell.references:
        if ref.cell.name not in [cell.name for cell in lib.cells]: # not very optimised
            add_children(ref.cell, lib)    

add_children(top, lib)

# would run DRC here if wanted to

# then do any inverting/converting to edge
flat_top = top.flatten()
mapping = {}

# convert all to polygons
for path in flat_top.paths:
    _ = flat_top.add(*path.to_polygons())

# sort by layers
for polygon in flat_top.polygons:
    layer_datatype = (polygon.layer, polygon.datatype)
    if layer_datatype in mapping.keys():
        mapping[layer_datatype].append(polygon)
    else:
        mapping[layer_datatype] = [polygon]

# merge all polygons for layer operations
for layer_datatype, polygons in mapping.items():
    mapping[layer_datatype] = gdstk.boolean(polygons, [], "or", layer=layer_datatype[0], datatype=layer_datatype[1])

# apply boundary operator
processed_layers = []
for layer in config.layers.values():
    ld = layer[:2]
    if ld not in processed_layers and layer[2] == "boundary":
        mapping[ld] = geom.flatten([geom.convert_to_boundary(p, config.boundary_width) for p in mapping[ld]])
    processed_layers.append(ld)

# put everthing in a new cell
flat_cell = gdstk.Cell("TOP")
for polygons in mapping.values():
    _ = flat_cell.add(*polygons)

# add the labels just in case they are used after all
for label in flat_top.labels:
    flat_cell.add(label)

# add all to library
flat_lib = gdstk.Library()
_ = flat_lib.add(flat_cell)

flat_lib.write_gds(outfile)