import numpy as np; import matplotlib.pyplot as plt

class RadiativeObject:

    _shape_aliases = {
        "puck": "puck",
        "pill": "puck",
        "cylinder": "puck",

        "block": "block",
        "cuboid": "block",
        "box": "block",
        "brick": "block"
    }

    def __init__(self, shape, **kwargs):
        shape = shape.strip().lower()

        if shape not in self._shape_aliases:
            raise ValueError(f"Unknown shape '{shape}'")

        self.shape = self._shape_aliases[shape]#allows different inputs, for example josh says "puck", kwaku says "pill"
        self.params = kwargs
        #kwargs makes it so that arguments are sorted by keyword rather than index i.e examplePuck = RadiativeObject("pill", depth=5, radius=1) or examplePuck = RadiativeObject("pill", radius=1, depth=5) both work

    def volume(self):
        if self.shape == "puck":
            r = self.params.get("radius")
            h = self.params.get("depth")
            if r is None or h is None:
                raise ValueError("Puck requires 'radius' and 'depth'")
            return np.pi * r**2 * h

        elif self.shape == "block":
            l = self.params.get("length")
            w = self.params.get("width")
            h = self.params.get("depth")
            if l is None or w is None or h is None:
                raise ValueError("Block requires 'length', 'width', and 'depth'")
            return l * w * h

        else:
            raise ValueError(f"Unknown shape '{self.shape}'")


starterpuck = RadiativeObject("pill", depth=5, radius=1)
print(f'The volume is {starterpuck.volume()}')
