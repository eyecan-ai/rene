import typing as t
from pathlib import Path

import numpy as np
from pipelime.items import PngImageItem
from pipelime.sequences import Sample, piped_sequence
from pipelime.sequences.pipes import PipedSequenceBase
from pydantic import Field, PrivateAttr

import rene.cli as c

X_CAMS = [4, 8, 15]
X_LITS = [2, 21, 34]


@piped_sequence
class BlackoutImages(
    PipedSequenceBase,
    title="blackout",
    underscore_attrs_are_private=True,
):
    image_key: str = Field("image", description="Image key")
    excluded_indices: t.Sequence = Field(..., description="Indices to exclude")
    relieved_indices: t.Sequence = Field([], description="Subindices to relieve")
    _image_shape: np.ndarray = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._image_shape = self.source[0][self.image_key]().shape  # type: ignore

    def get_sample(self, idx: int) -> Sample:
        sample = self.source[idx]
        if idx in self.excluded_indices:
            image_item = PngImageItem(np.zeros(self._image_shape, dtype=np.uint8))
            sample = sample.set_value(self.image_key, image_item)

        return sample


@c.command(title="blackout-scene")
def blackout(
    input_folder: Path = c.Field(..., description="Input scene folder"),
    output_folder: Path = c.Field(..., description="Output scene folder"),
):
    """
    Given a scene with train, val and test images, substitute the test images with black ones
    """

    from pipelime.sequences import SamplesSequence

    # loop over the subfolders of the input folder
    subs = [x for i, x in enumerate(sorted(input_folder.iterdir())) if i not in X_LITS]

    for sub in subs:
        uf = SamplesSequence.from_underfolder(sub)
        uf = uf.blackout(excluded_indices=X_CAMS)  # type: ignore
        uf.to_underfolder(output_folder / sub.name).run()
