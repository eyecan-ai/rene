import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="convert-to-jpg")
def convert(
    input_folder: Path = c.Field(..., description="Input scene folder"),
    output_folder: Path = c.Field(..., description="Output scene folder"),
):
    """
    Given scenes folder, convert images in jpg
    """

    import numpy as np
    from pipelime.items import JpegImageItem
    from pipelime.sequences import Sample, SamplesSequence
    from pipelime.stages import SampleStage
    from pydantic import Field

    from rene.utils import DATA_KEYS

    class PngToJpeg(SampleStage, title="png-to-jpeg"):
        """Convert each sample in jpg sample"""

        im_keys: t.Sequence[str] = Field(["image"], description="Key of ims to resize.")

        def __call__(self, s: Sample) -> Sample:
            # converting the image
            for key in self.im_keys:
                image: np.ndarray = s[key]()  # type: ignore
                image_item = JpegImageItem(image)

                s = s.set_item(key, image_item)

            return s

    # loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if x.name in DATA_KEYS]

    for sub in subs:
        lsets = [x for x in sub.iterdir()]
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset)
            uf = uf.map(PngToJpeg(im_keys=["image"]))
            uf.to_underfolder(output_folder / sub.name / lset.name).run()
