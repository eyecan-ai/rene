import typing as t
from pathlib import Path

from pipelime.sequences import SamplesSequence as SS
from pipelime.stages import StageRemap
from pydantic import BaseModel, Field, PrivateAttr
from rich.progress import track

from rene.utils.stages import ResizeStage


class ReneDataset(BaseModel):
    """
    A class to lazy load the ReNé dataset

    Args:
        input_folder (Path): ReNé parent folder

    Examples:
        >>> rene = ReneDataset(input_folder=Path("/path/to/rene_parent_folder"))
        >>> sample = rene["apple"][12][34]
        >>> image = sample["image"]()
    """

    input_folder: Path = Field(..., description="ReNé parent folder")
    image_max_size: int = Field(1440, description="Resize images to smallest max size")
    thumb_max_size: int = Field(1440, description="Resize thumbs to smallest max size")

    _KEYS_TO_LOAD: t.Sequence = PrivateAttr(
        [
            "apple",
            "plant",
            "fruits",
            # "empty", # Not included
            "lego",
            "tapes",
            "wooden",
            "cheetah",
            "shark",
            "lunch",
            "reflective",
            "flipflop",
            "robotoy",
            "cube",
            "trucks",
            "garden",
            "stegosaurus",
            "dinosaurs",
            "helicopters",
            "savannah",
            "kittens",
        ]
    )
    _TEST_CAMS = [4, 8, 15]
    _TEST_LIGHTS = [2, 21, 34]
    _IM_SZ = (1440, 1080)

    _data: t.MutableMapping[str, t.List[SS]] = PrivateAttr()

    def __getitem__(self, key: str) -> t.List[SS]:
        """
        Implement the __getitem__ method to allow for indexing into the dataset.

        Args:
            key (str): The key to retrieve from the dataset.

        Returns:
            List[SamplesSequence]: The list of lightsets SamplesSequence corresponding to the key.
        """
        return self._data[key]

    def __init__(self, **kwargs) -> None:
        """
        Lazy load the entire dataset.

        Args:
            input_folder (Path): ReNé parent folder.
        """
        super().__init__(**kwargs)

        i_f = self._IM_SZ[0] // self.image_max_size
        t_f = self._IM_SZ[0] // self.thumb_max_size

        rs = ResizeStage(target_size=(self._IM_SZ[0] // i_f, self._IM_SZ[1] // i_f))  # type: ignore
        rs_t = ResizeStage(target_size=(self._IM_SZ[0] // t_f, self._IM_SZ[1] // t_f))  # type: ignore
        remap = StageRemap(remap={"image": "thumb"}, remove_missing=True)

        # Loop over the subfolders of the input folder
        scenes = [x for x in list(sorted(self.input_folder.iterdir())) if x.is_dir()]

        # We lazy load the entire dataset
        self._data = {}
        for s in track(scenes, description="Lazy Loading Dataset..."):
            if s.name not in self._KEYS_TO_LOAD:
                continue
            lsets = [x for x in list(sorted(s.iterdir()))]
            ufs_t = [SS.from_underfolder(ls).map(rs_t).map(remap) for ls in lsets]
            ufs_i = [SS.from_underfolder(ls).map(rs) for ls in lsets]
            ufs_data = [ufs_i[i].zip(ufs_t[i]) for i in range(len(ufs_i))]
            self._data[s.name] = ufs_data

    def keys(self) -> t.List[str]:
        """
        Return the available keys of the dataset.

        Returns:
            List[str]: The keys of the dataset.
        """
        return list(self._data.keys())

    def get_test_cams(self) -> t.List[int]:
        """
        Return the test cameras indices.
        """
        return self._TEST_CAMS

    def get_test_lights(self) -> t.List[int]:
        """
        Return the test lights indices.
        """
        return self._TEST_LIGHTS

    def __repr__(self) -> str:
        """
        Override the __repr__ method to show the keys in the dataset.

        Returns:
            str: A string representation of the keys in the dataset.
        """
        return f"ReneDataset(available_keys={list(self._data.keys())})"
