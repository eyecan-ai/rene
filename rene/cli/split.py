import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="blackout-scene")
def blackout(
    input_folder: Path = c.Field(..., alias="i", description="ReNé priv parent folder"),
    output_folder: Path = c.Field(..., alias="o", description="ReNé pub parent folder"),
):
    """
    Given a scene with train, val and test images, substitute the test images with black ones
    """
    import numpy as np
    from pipelime.items import PngImageItem
    from pipelime.sequences import Sample, SamplesSequence, piped_sequence
    from pipelime.sequences.pipes import PipedSequenceBase
    from pydantic import Field, PrivateAttr

    from rene.utils import DATA_KEYS

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

    # loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if x.name in DATA_KEYS]

    for sub in subs:
        lsets = [x for i, x in enumerate(sorted(sub.iterdir()))]
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset)
            uf = uf.blackout(excluded_indices=X_CAMS)  # type: ignore
            if int(lset.name.removeprefix("lset")) in X_LITS:
                uf = uf.blackout(excluded_indices=list(range(len(uf))))  # type: ignore
            uf.to_underfolder(output_folder / sub.name / lset.name).run()
