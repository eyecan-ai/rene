from pathlib import Path

import rene.cli as c


@c.command(title="extract")
def extract(
    input_folder: Path = c.Field(..., alias="i", description="Folder with ReNé zips"),
    output_folder: Path = c.Field(..., alias="o", description="ReNé parent folder"),
):
    import zipfile

    from rene.utils import DATA_KEYS

    # Loop over the subfolders of the input folder
    scenes = [
        x
        for x in list(sorted(input_folder.iterdir()))
        if x.stem.split("_")[0] in DATA_KEYS and x.suffix == ".zip"
    ]

    for scene in scenes:
        print(f"Extracting: {scene.name}")
        with zipfile.ZipFile(scene, "r") as zip_ref:
            zip_ref.extractall(output_folder / scene.stem.split("_")[0])


@c.command(title="compress")
def compress(
    input_folder: Path = c.Field(..., alias="i", description="ReNé parent folder"),
    output_folder: Path = c.Field(..., alias="i", description="Folder with ReNé zips"),
):
    import zipfile

    from rich import print

    from rene.utils import DATA_KEYS

    output_folder.mkdir(exist_ok=True)

    # loop over the subfolders of the input folder
    subs = [
        x
        for x in list(sorted(input_folder.iterdir()))
        if x.name.split("_")[0] in DATA_KEYS and x.is_dir()
    ]

    for sub in subs:
        print(f"Compressing: {sub.name}")
        with zipfile.ZipFile(output_folder / f"{sub.name}_public.zip", "w") as zip_ref:
            for fp in sub.rglob("*"):
                zip_ref.write(fp, arcname=fp.relative_to(sub))
