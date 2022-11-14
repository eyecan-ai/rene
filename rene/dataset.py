import os
from pipelime.sequences import SamplesSequence
from typing import List, Optional
from pathlib import Path
import cv2
import numpy as np
import rich


class ReNeDataset:
    CAMERA_ORDERED_INDICES = [
        48,
        47,
        46,
        45,
        44,
        43,
        42,
        41,
        40,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        30,
        29,
        28,
        27,
        26,
        25,
        24,
        23,
        22,
        15,
        14,
        16,
        17,
        18,
        19,
        20,
        21,
        13,
        12,
        11,
        10,
        9,
        8,
        3,
        4,
        5,
        6,
        7,
        1,
        0,
        2,
        49,
    ]

    def __init__(self, root_folder: str, reorder_camera_indices: bool = True):
        self._root_folder = root_folder
        self._reorder_camera_indices = reorder_camera_indices
        objects_folders = self._scandirs(root_folder)

        self._objects = []
        for object_folder in objects_folders:
            lightsets_folders = self._scandirs(object_folder)

            self._objects.append(
                [
                    SamplesSequence.from_underfolder(lightset_folder)
                    for lightset_folder in lightsets_folders
                ]
            )

    def camera_index(self, raw_index: int):
        if self._reorder_camera_indices:
            return self.CAMERA_ORDERED_INDICES[raw_index]
        else:
            return raw_index

    def num_objects(self):
        return len(self._objects)

    def num_lights(self, object_idx: int = 0):
        return len(self._objects[object_idx])

    def num_cameras(self, object_idx: int = 0, light_idx: int = 0):
        return len(self._objects[object_idx][light_idx])

    def _scandirs(self, folder: str):
        return list(sorted([f.path for f in os.scandir(folder) if f.is_dir()]))

    def get(self, object_idx: int, light_idx: int, camera_idx: int, key: str = "image"):
        camera_idx = self.camera_index(camera_idx)
        sample = self._objects[object_idx][light_idx][camera_idx]
        return sample[key]()


class QualitativeMemphisDataset:
    HARDTEST = "hardtest"
    EASYTEST = "easytest"

    CONVERSIONS = {
        "depth": lambda x: cv2.cvtColor(
            cv2.applyColorMap(
                255 - cv2.normalize(x, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U),
                cv2.COLORMAP_MAGMA,
            ),
            cv2.COLOR_BGR2RGB,
        ),
        "diff": lambda x: cv2.cvtColor(
            cv2.applyColorMap(
                cv2.normalize(x, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U),
                cv2.COLORMAP_JET,
            ),
            cv2.COLOR_BGR2RGB,
        ),
        "shadows": lambda x: cv2.normalize(x, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U),
    }

    def __init__(self, root_folder: str):
        self._root_folder = root_folder

        self._subfolders = self._scandirs(root_folder)
        self._names = [Path(subfolder).name for subfolder in self._subfolders]
        self._names_and_subs = zip(self._names, self._subfolders)

        self._files_maps = {}
        for object_name, folder in self._names_and_subs:
            self._files_maps[object_name] = {
                self.EASYTEST: self._files(os.path.join(folder, self.EASYTEST)),
                self.HARDTEST: self._files(os.path.join(folder, self.HARDTEST)),
            }

    def splits(self):
        return [self.EASYTEST, self.HARDTEST]

    def objects_names(self):
        return list(self._files_maps.keys())

    def num_objects(self):
        return len(self._subfolders)

    def num_items(self, object_name: str, split: Optional[str] = None):
        return len(self._files_maps[object_name][split])

    def get(
        self,
        object_name: str,
        index: int = 0,
        split: Optional[str] = None,
        keys: List[str] = ["gt", "image", "shadows", "depth"],
    ):
        if split is None:
            split = self.EASYTEST

        folder = os.path.join(self._root_folder, object_name, split)
        filesmap = self._files(folder)

        if index not in filesmap:
            raise Exception("Index not found")

        slot = filesmap[index]

        items_map = filesmap[index]

        output = {}
        for key in keys:
            if key.startswith("$"):
                command, args = key.replace("$", "").split("|")
                command_keys = args.split(",")
                command_paths = list(map(lambda x: items_map[x], command_keys))
                image = self._image_function(command, command_paths)
                if image is not None:
                    output[command] = image

            else:
                output[key] = self._read_image(items_map[key])

        return output

    def get_stack(
        self,
        object_name: str,
        index: int = 0,
        split: Optional[str] = None,
        keys: List[str] = ["gt", "image", "shadows", "depth"],
    ):
        images = self.get(object_name, index, split, keys)
        stack = []
        for image_name, image in images.items():

            for key, conversion in self.CONVERSIONS.items():
                if key in image_name:
                    image = conversion(image)

            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            stack.append(image)

        stack = np.hstack(stack)
        return stack

    def _image_function(self, func: str, paths: List[str]):
        images = [self._read_image(x) for x in paths]
        if func == "diff":

            images = list(map(lambda x: x.astype(np.float32), images))
            diff_image = np.abs(images[0] - images[1])
            diff_image = diff_image.astype(np.uint8)
            single_channel = diff_image  # (single_channel * 255).astype(np.uint8)

            return single_channel
        return None

    def _read_image(self, path: str):
        import imageio

        return imageio.imread(path)

    def _files(self, folder: str):
        raw_files = list(sorted([f.path for f in os.scandir(folder) if f.is_file()]))
        files_map = {}

        for file in raw_files:
            try:
                file_name = Path(file)
                splits = file_name.stem.split("_")
                index = int(splits[0])
                item = splits[1]

                if index not in files_map:
                    files_map[index] = {}

                files_map[index][item] = file
            except:
                pass

        return files_map

    def _scandirs(self, folder: str):
        return list(sorted([f.path for f in os.scandir(folder) if f.is_dir()]))
