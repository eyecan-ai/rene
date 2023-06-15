import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="filter-calibration")
def filter_calibration(
    input_folder: Path = c.Field(..., description="Input folder with scenes"),
    output_folder: Path = c.Field(..., description="Output scenes folder"),
    name: t.Optional[str] = c.Field(None, description="Name of the single scene"),
):
    """
    Copy calibration files to the scene folder
    """

    from pipelime.sequences import SamplesSequence
    from pipelime.stages import StageRemap

    from rene.utils import DATA_KEYS

    names = DATA_KEYS if name is None else [name]

    # loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if x.name in names]

    for sub in subs:
        lsets = [x for x in sub.iterdir()]
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset)
            remap_keys = StageRemap(
                remap={
                    "light": "light",
                    "image": "image",
                    "optimized_camera": "camera",
                    "optimized_pose": "pose",
                },
                remove_missing=True,
            )
            uf = uf.map(remap_keys)
            uf.to_underfolder(output_folder / sub.name / lset.name).run()
