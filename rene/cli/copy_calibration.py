import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="copy-calibration")
def copy_calib(
    input_folder: Path = c.Field(..., description="Input folder with scenes"),
    input_calibration: Path = c.Field(..., description="Input folder with calibration"),
    output_folder: Path = c.Field(..., description="Output scenes folder"),
    name: t.Optional[str] = c.Field(None, description="Name of the single scene"),
):
    """
    Copy calibration files to the scene folder
    """

    from pipelime.sequences import SamplesSequence

    from rene.utils import DATA_KEYS

    names = DATA_KEYS if name is None else [name]

    # Loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if x.name in names]
    calib = SamplesSequence.from_underfolder(input_calibration)

    for sub in subs:
        lsets = [x for x in sub.iterdir()]
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset)
            uf = uf.zip(calib.repeat(len(uf)))
            uf.to_underfolder(output_folder / sub.name / lset.name).run()


@c.command(title="fix-calib-cam")
def fix_calib_cam(
    input_folder: Path = c.Field(..., description="Input folder with scenes"),
    output_folder: Path = c.Field(..., description="Output scenes folder"),
):
    """
    Copy calibration files to the scene folder
    """

    from pipelime.items import YamlMetadataItem
    from pipelime.sequences import SamplesSequence

    from rene.utils import DATA_KEYS

    # Loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if x.name in DATA_KEYS]
    # calib = SamplesSequence.from_underfolder(input_calib)

    for sub in subs:
        lsets = [x for x in sub.iterdir()]
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset)
            camera_bad = uf[0]["camera"]()
            intrinics_bad = camera_bad["intrinsics"]  # type: ignore
            distortion_coeffs_bad = intrinics_bad["dist_coeffs"]
            distortion_coeffs_good = [distortion_coeffs_bad[i][0] for i in range(5)]
            intrinics_good = intrinics_bad.copy()
            intrinics_good["dist_coeffs"] = distortion_coeffs_good
            camera_good = {"intrinsics": intrinics_good}

            camera_item = YamlMetadataItem(camera_good, shared=True)
            new_seq = []
            for sample in uf:
                new_seq.append(sample.set_item("camera", camera_item))

            new_uf = SamplesSequence.from_list(new_seq)
            new_uf.to_underfolder(output_folder / sub.name / lset.name).run()
