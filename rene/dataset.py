import os
from pipelime.sequences import SamplesSequence


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
        14,
        15,
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
        2,
        1,
        0,
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
