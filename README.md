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
You can always download the dataset from [this Google Drive Folder](https://drive.google.com/file/d/1eOWV5jrcOyNBT3DGv2rHQC_OnD3BsHVk/view?usp=sharing) and extract the files contained in the zip archive in `/path/to/rene_parent_folder`. The structure of the extracted folder should be the following:
```
📂 rene_parent_folder
├── 📁 apple
├── 📁 cheetah 
├── 📁 cube 
...
├── 📁 tapes
├── 📁 trucks
└── 📁 wooden 
```

## 📝 Dataset structure
Each scene folder contains the following files:
```
📂 rene_parent_folder
├── 📂 apple
│   ├── 📂 lset000
│       ├── 📃️ camera.yml
│       ├── 📄 light.txt 
│       ├── 📂 data
│           ├── 🖼️ 00000_image.png
│           ├── 📄 00000_pose.txt
│           ...
│           ├── 🖼️ 00048_image.png
│           └── 📄 00049_pose.txt
│   ├── 📁 lset001
│   ...
│   └── 📁 lset039
...
```

Additional notes:
- Poses `XXXXX_poses.txt` and `light.txt` are 4x4 homogeneous matrices $^wT_c$ that transform points expressed in the camera reference frame $c$ to points expressed in the world reference frame $w$, such that: $^wp={^wT_c} \cdot {^cp}$. [Upward: +Z]
- Camera parameters `camera.yml` are the one returned by OpenCV's `calibrateCamera()` function, convention is the one of COLMAP/OpenCV. [Forward: +Z, Up: -Y, Right: +X].
- Test images are blacked out and their indices are following the table on the paper.
- We also recovered an empty scene (only lighting change, no objects) but it's not officially included in the dataset, it's not used in the paper and the following scripts won't support it natively.


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
import matplotlib.pyplot as plt

from rene.utils.loaders import ReneDataset

# Lazy load the dataset
rene = ReneDataset(input_folder="/path/to/rene_parent_folder")

# To get a sample, you can do the following:
sample = rene["cube"][18][36]  # <- scene=cube, light_pose=18, camera_pose=36

# Each sample contains [camera, image, pose, light] keys
# To actually load an image you can do this:
image = sample["image"]()  # <- Notice the `()` at the end!

# And use the item as you wish
plt.imshow(image)
plt.show()

```
Here it's (or will be) a list of more advanced examples:
<details>
  <summary>Help Script for Testing</summary>
Here is a sample script that show how the test images can be generated, given your trained network `MyCoolModel`:

```python
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
rene = ReneDataset(input_folder="/path/to/rene_parent_folder")

# Define the output folder
output_folder = Path("/tmp/rene_test_folder")
output_folder.mkdir(exist_ok=True)

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
```
This will save in the `/path/to/rene_test_folder` the files ready for the next step, benchmarking!

</details>
<br></br>

To see more advanced examples you can always check the `rene` library.


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
