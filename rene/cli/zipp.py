from pathlib import Path

import rene.cli as c


@c.command(title="extract")
def extract(
    input_folder: Path = c.Field(..., description="Input scene folder"),
    output_folder: Path = c.Field(..., description="Output scene folder"),
):
    import zipfile

    from rene.utils import DATA_KEYS

    # loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if str(x.name).endswith("_public")]

    for sub in subs:
        if sub.name in DATA_KEYS:
            with zipfile.ZipFile(sub, "r") as zip_ref:
                zip_ref.extractall(output_folder / sub.name)


@c.command(title="compress")
def compress(
    input_folder: Path = c.Field(..., description="Input scene folder"),
    output_folder: Path = c.Field(..., description="Output scene folder"),
):
    import zipfile

    from rich import print

    from rene.utils import DATA_KEYS

    output_folder.mkdir(exist_ok=True)

    # loop over the subfolders of the input folder
    subs = [x for x in input_folder.iterdir() if str(x.name).endswith("_public")]

    for sub in subs:
        print(f"Compressing: {sub.name}")
        if str(sub.name).replace("_public", "") in DATA_KEYS:
            with zipfile.ZipFile(output_folder / f"{sub.name}.zip", "w") as zip_ref:
                for fp in sub.rglob("*"):
                    zip_ref.write(fp, arcname=fp.relative_to(sub))
                    zip_ref.write(fp, arcname=fp.relative_to(sub))
