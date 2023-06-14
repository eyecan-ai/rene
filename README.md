# Relight My Nerf - A Dataset for Novel View Synthesis and Relighting of Real World Objects

This package contains commands to manage the dataset for the Relight My Nerf project. The architecture of the network is not included in this package, nor the training scripts. This package is only for managing the dataset.

## 👷‍♀️ Install the management package
To install the package, run the following command in a python venv:
```bash
git clone git@github.com:eyecan-ai/rene.git
cd rene
pip install .
```
It has been tested with python 3.9 on Ubuntu 22.04, should work even with python >= 3.8 and hopefully in another OS.

## ⬇️ Download the dataset
To download the dataset, run the following command:
```bash
rene download +o /path/to/rene_zips_folder
```
⚠️ Due to google drive limitations, it is possible that the above script will fail after downloading half of the scenes (or less). If the download fails, you can always download manually the remaining scenes from [this Google Drive Folder](https://drive.google.com/drive/folders/1ONYpV6OkmKNQuchfQSkOhuh8gBJKfYY8?usp=drive_link) and place the zip files in `/path/to/rene_zips_folder`.

Mind that:
- Poses are annotated in COLMAP/OpenCV coordinate system convention: [+Z points upward]
- Camera matrix is the one returned by OpenCV's `calibrateCamera()` function: [Forward: +Z, Up: -Y, Right: +X].
- Test images are blacked out and their indices are following the table on the paper.
- We also recovered an empty scene (only lighting change, no objects), it's the one called "empty_public.zip".

## 📦 Extract the dataset
To extract the dataset, run the following command:
```bash
rene extract +i /path/to/rene_zips_folder +o /path/to/rene_parent_folder
```
If the extraction fails, you can always extract the dataset manually from the zip files and place the folders in `/path/to/rene_parent_folder` such as:
`apple_public.zip -> /path/to/rene_parent_folder/apple/lset000`

## 👁️ Show the dataset
As a check if everying went well, you can show the dataset with the following command:
```bash
rene show +i /path/to/rene_parent_folder
```
This will show a window similar to the following:

https://github.com/eyecan-ai/rene/assets/23316277/51fac737-05ed-4d20-bdac-3687f44f4f1d

## 🛼 Handle the dataset
We use `pipelime-python` to handle the dataset, it's automatically installed when you install the package, but you can find the documentation [here](https://pipelime-python.readthedocs.io/en/latest/).

A simple script to load the dataset is the following:
```python
from pathlib import Path

from pipelime.sequences import SamplesSequence
from rich import print
from rich.progress import track
import matplotlib.pyplot as plt

INPUT_FOLDER = Path("/path/to/rene_parent_folder")
SCENE_NAME = "cube"

# Loop over the subfolders of the input folder
scenes = [x for x in list(sorted(INPUT_FOLDER.iterdir()))]

# We lazy load the entire dataset
rene = {}
for scene in track(scenes, description="Lazy Loading Dataset..."):
    lsets = [x for x in list(sorted(scene.iterdir()))]
    rene[scene.name] = [SamplesSequence.from_underfolder(lset) for lset in lsets]

# To actually load a sample, you can do the following:
sample = rene[SCENE_NAME][18][36]
camera_params = sample["camera"]()  # <- Notice the `()` at the end!
image = sample["image"]()
camera_pose = sample["pose"]()
light_pose = sample["light"]()

print(f"Camera Params: {camera_params}")
print(f"Image shape: {image.shape}")
print(f"Camera Pose: {camera_pose}")
print(f"Light Pose: {light_pose}")
print(f"Light Pose: {light_pose}")

plt.imshow(image)
plt.show()

```
To see a more advanced example you can check the commands inside `rene/cli` files.

## 🧪 Testing your Network
Here is a sample script that show how the test images can be generated, given your trained network `MyCoolModel`:
```python
from pathlib import Path

import imageio as iio
import numpy as np
from rich import print
from rich.progress import track

from rene.utils import DATA_KEYS, X_CAMS
from rene.utils.loaders import lazy_load

INPUT_FOLDER = Path("/path/to/rene_parent_folder")
OUTPUT_FOLDER = Path("/path/to/rene_test_folder")


# Define you cool model here
class MyCoolModel:
    # This model is just a random image generator
    def __call__(self, camera, *args):
        w, h = camera["intrinsics"]["image_size"]
        return (np.random.standard_normal([h, w, 3]) * 255).astype(np.uint8)


# Create the output folder
OUTPUT_FOLDER.mkdir(exist_ok=True, parents=True)

# Load the dataset
rene = lazy_load(INPUT_FOLDER)

my_cool_model = MyCoolModel()  # <--- THIS IS YOUR CUSTOM MODEL

# We iterate over the dataset, we predict and save the images
for key in DATA_KEYS:
    print(f"Testing [bold][green]{key}[/green][/bold]:")
    for cam in X_CAMS:
        for lit in track(range(40), description=f"[yellow]camera {cam}[/yellow]"):
            s = rene[key][lit][cam]

            ### YOUR CUSTOM PREDICTION ----------------------------------
            pred = my_cool_model(s["camera"](), s["pose"](), s["light"]())
            ### YOUR CUSTOM PREDICTION ----------------------------------

            filename = f"{key}_{str(lit).zfill(2)}_{str(cam).zfill(2)}.png"
            iio.imwrite(OUTPUT_FOLDER / filename, pred, compress_level=4)
```
This will save in the `OUTPUT_FOLDER` the files ready for the next step, benchmarking!

## 🪑 Contribute to the Benchmark
To send your test images you will need to upload and send the link of a zip file with the following structure:

```
📦 rene_test_images.zip
├── 🖼️ apple_00_04.png
├── 🖼️ apple_00_08.png
├── 🖼️ apple_00_15.png
...
├── 🖼️ apple_39_04.png
├── 🖼️ apple_39_08.png
├── 🖼️ apple_39_15.png
├── 🖼️ cheetah_00_04.png
...
├── 🖼️ cheetah_39_15.png
├── 🖼️ cube_00_04.png
...
```
The format for each image is: `{scene_name}_{light_idx}_{cam_idx}.png` and they need to be at the root level of the zip file.
Each scene will have 111 images for the easy test and 9 for the hard test, for a total of 120 * 20 = 2400 images, your zip archive should contain exactly this number of files.
At the time of writing, the link of your zip file should be sent to any email address with the suffix `eyecan.ai` present in the paper.

## 🖋️ Citation
If you find this dataset useful, please give us a github star, if you were crazy enough to download the dataset and it was useful to you in some way for your work, it would be great if you would cite us:
```
@InProceedings{Toschi_2023_CVPR,
          author    = {Toschi, Marco and De Matteo, Riccardo and Spezialetti, Riccardo and De Gregorio, Daniele and Di Stefano, Luigi and Salti, Samuele},
          title     = {ReLight My NeRF: A Dataset for Novel View Synthesis and Relighting of Real World Objects},
          booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
          month     = {June},
          year      = {2023},
          pages     = {20762-20772}
        }
```
