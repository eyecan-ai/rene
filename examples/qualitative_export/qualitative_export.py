import typer
import cv2
from typing import Tuple, Union, List
import rich
import numpy as np
from pathlib import Path
from rene.dataset import QualitativeMemphisDataset
import albumentations as A


def qualitative_export(
    input_folder: str = typer.Option(
        ...,
        "--input-folder",
        "-i",
        help="Path to the input folder",
    ),
    output_folder: str = typer.Option(
        ...,
        "--output-folder",
        "-o",
        help="Path to the output folder",
    ),
    resize: int = typer.Option(
        300,
        "--resize",
        "-r",
        help="Image resize [smallest size]",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Debug mode",
    ),
):

    # Output folder
    output_folder = Path(output_folder)
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    # Dataset
    qualitatives = QualitativeMemphisDataset(input_folder)

    # T
    T = A.Compose(
        [
            A.SmallestMaxSize(max_size=resize),
            A.PadIfNeeded(
                min_height=None,
                min_width=None,
                pad_height_divisor=2,
                pad_width_divisor=2,
                border_mode=cv2.BORDER_REFLECT,
            ),
        ]
    )

    # #######################################
    # EXAMPLE OF CFG
    # cfg = {
    #     "items": ["gt", "image", "shadows", "depth", "$diff|image,gt"],
    #     "objects": {
    #         "apple_TM": {"easytest": [0, 1, 2], "hardtest": [3, 4, 5]},
    #         "tapes_TM": {"easytest": [0, 1, 2], "hardtest": [3, 4, 5]},
    #     },
    # }
    # #######################################

    #######################################
    # EXAMPLE OF PROCEDURAL CFG
    cfg = {
        "items": ["gt", "image", "shadows", "depth", "$diff|image,gt"],
        # "items": ["gt", "image", "shadows"],
        "objects": {},
    }
    easy_indices_size = 111
    hard_indices_size = 9
    picked_samples = 3

    #######################################
    # #Random indices
    # easy_indices = np.random.permutation(range(easy_indices_size))[:picked_samples]
    # hard_indices = np.random.permutation(range(hard_indices_size))[:picked_samples]

    # #Picked indices
    easy_indices = [33, 67, 101]
    hard_indices = [0, 4, 8]
    #######################################

    print(easy_indices, hard_indices)
    for object_name in qualitatives.objects_names():
        cfg["objects"][object_name] = {
            qualitatives.EASYTEST: easy_indices,
            qualitatives.HARDTEST: hard_indices,
        }
    #######################################

    # Generation
    for obj_name in cfg["objects"].keys():
        for split_name in cfg["objects"][obj_name].keys():
            for idx in cfg["objects"][obj_name][split_name]:
                rich.print(obj_name, split_name, idx)
                rich.print(qualitatives.num_items(obj_name, split_name))
                stack = qualitatives.get_stack(
                    obj_name,
                    index=idx,
                    split=split_name,
                    keys=cfg["items"],
                )

                stack = T(image=stack)["image"]

                if debug:
                    cv2.imshow("stack", cv2.cvtColor(stack, cv2.COLOR_RGB2BGR))
                    cv2.waitKey(0)

                # save image
                output_path = (
                    output_folder / f"{split_name}_{obj_name}_{idx}_{resize}.png"
                )
                cv2.imwrite(str(output_path), cv2.cvtColor(stack, cv2.COLOR_RGB2BGR))
                print(output_path)


if __name__ == "__main__":
    typer.run(qualitative_export)
