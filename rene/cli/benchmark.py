import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="view-format")
def check_format():
    from rene.utils import DATA_KEYS, X_CAMS, X_LITS

    for key in DATA_KEYS:
        for cam in X_CAMS:
            for i in range(40):
                print(f"{key}_{str(i).zfill(2)}_{str(cam).zfill(2)}.png")


@c.command(title="uf-to-simple")
def convert_scene(
    input_folder: Path = c.Field(..., alias="i", description="ReNé test in uf"),
    output_folder: Path = c.Field(..., alias="o", description="ReNé test merged"),
):
    import shutil

    easy_folder = input_folder / "easytest"
    hard_folder = input_folder / "hardtest"

    output_folder.mkdir(parents=True, exist_ok=True)

    from rene.utils import DATA_KEYS, X_CAMS, X_LITS

    easy_list = []
    hard_list = []
    for cam in X_CAMS:
        for i in range(40):
            if i in X_LITS:
                hard_list.append(f"{str(i).zfill(2)}_{str(cam).zfill(2)}")
            else:
                easy_list.append(f"{str(i).zfill(2)}_{str(cam).zfill(2)}")

    for folder, map_list in zip([easy_folder, hard_folder], [easy_list, hard_list]):
        for file in folder.iterdir():
            if file.suffix == ".png":
                splits = file.name.split("_")
                idx = int(splits[0])
                key = splits[1].split(".")[0]
                if key == "image":
                    shutil.copyfile(
                        file,
                        output_folder
                        / f"{input_folder.name.split('_')[0]}_{map_list[idx]}.png",
                    )
