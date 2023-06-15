"""
Here is a sample script that show how the test images can be generated, given your trained network
"""
from pathlib import Path

import imageio as iio
import numpy as np
from rich import print
from rich.progress import track

from rene.utils.loaders import ReneDataset


# Define your cool model here
class MyCoolModel:
    # This model is just a random image generator
    def __call__(self, camera, *args):
        w, h = camera["intrinsics"]["image_size"]
        return (np.random.standard_normal([h, w, 3]) * 255).astype(np.uint8)


# Lazy load the dataset
rene = ReneDataset(input_folder="/path/to/rene_parent_folder")  # <--- CHANGE THIS

# Define the output folder
output_folder = Path("/tmp/rene_test_folder")  # <--- AND CHANGE THIS
output_folder.mkdir(exist_ok=True, parents=True)

my_cool_model = MyCoolModel()  # <--- THIS IS YOUR CUSTOM MODEL

# We iterate over the dataset, we predict and save the images
for key in rene.keys():
    print(f"Testing [bold][green]{key}[/green][/bold]:")
    for cam in rene.get_test_cams():
        for lit in track(range(40), description=f"[yellow]camera {cam}[/yellow]"):
            s = rene[key][lit][cam]

            ### YOUR CUSTOM PREDICTION ----------------------------------
            pred = my_cool_model(s["camera"](), s["pose"](), s["light"]())
            ### YOUR CUSTOM PREDICTION ----------------------------------

            filename = f"{key}_{str(lit).zfill(2)}_{str(cam).zfill(2)}.png"
            iio.imsave(output_folder / filename, pred, compress_level=4)
