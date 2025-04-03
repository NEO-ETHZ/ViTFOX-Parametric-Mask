layers = {
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
UVL = 2
EBL = 0.05

# general design parameters
wire_width = 3
boundary_width = 1

pad_dim = 50

pad_device_spacing = 10