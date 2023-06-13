# Relight My Nerf - A Dataset for Novel View Synthesis and Relighting of Real World Objects

This package contains commands to manage the dataset for the Relight My Nerf project. The architecture of the network is not included in this package, nor the training scripts. This package is only for managing the dataset.

## Install the management package
To install the package, run the following command:
```bash
git clone git@github.com:eyecan-ai/rene.git
pip install .
```

## Download the dataset
To download the dataset, run the following command:
```bash
rene download +o /path/to/rene_zips_folder
```
If the download fails, you can always download the dataset manually from [this Google Drive Folder](https://drive.google.com/drive/folders/1ONYpV6OkmKNQuchfQSkOhuh8gBJKfYY8?usp=drive_link) and place the zip files in `/path/to/rene_zips_folder`.

Mind that:
- Poses are annotated in OpenCV coordinate system convention.
- Camera matrix is the one returned by OpenCV's `calibrateCamera()` function.
- Test images are blacked out and their indices are following the table on the paper.
- We also recovered an empty scene (only lighting change, no objects), it's the one called "empty_public.zip".

## Extract the dataset
To extract the dataset, run the following command:
```bash
rene extract +i /path/to/rene_zips_folder +o /path/to/rene_parent_folder
```
If the extraction fails, you can always extract the dataset manually from the zip files and place the folders in `/path/to/rene_parent_folder` such as:
`apple_public.zip -> /path/to/rene_parent_folder/apple/lset000`

## Show the dataset
As a check if everying went well, you can show the dataset with the following command:
```bash
rene show +i /path/to/rene_parent_folder
```
This will show a window similar to the following:

https://github.com/eyecan-ai/rene/assets/23316277/51fac737-05ed-4d20-bdac-3687f44f4f1d

## Handle the dataset
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

## Citation
If you use this dataset, please cite the following paper:
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
