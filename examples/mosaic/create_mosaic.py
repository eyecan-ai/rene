import typer
import os
import cv2
from typing import Tuple, Union, List
import yaml
import rich
import pydantic
import numpy as np
from pathlib import Path
from rene.dataset import ReNeDataset


class MosaicConfig(pydantic.BaseModel):
    object_id: Union[int, List[int]]
    cameras: list
    lights: list
    crop: Tuple[int, int, int, int] = [-1, -1, -1, -1]
    crop_type: str = "tl"  # tl | center
    borders: int = 5
    borders_color: Tuple[int, int, int] = (255, 255, 255)
    outer_border: bool = False


def name(
    input_folder: str = typer.Option(
        ...,
        "--input-folder",
        "-i",
        help="Path to the input folder",
    ),
    cfg_path: str = typer.Option(
        ...,
        "--cfg-path",
        "-c",
        help="Path to the config file",
    ),
    transpose: bool = typer.Option(
        False,
        "--transpose",
        "-t",
        help="Transpose the image",
    ),
    output_folder: str = typer.Option(
        ...,
        "--output-folder",
        "-o",
        help="Path to the output folder",
    ),
):

    # Output folder
    output_folder = Path(output_folder)
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    # Rene Browser
    rene = ReNeDataset(input_folder, reorder_camera_indices=False)

    # load yaml
    cfg = MosaicConfig(**(yaml.load(open(cfg_path, "r"), Loader=yaml.FullLoader)))

    # manage multiple ids
    if isinstance(cfg.object_id, int):
        if cfg.object_id == -1:
            cfg.object_id = list(range(rene.num_objects()))
            print("IDS", cfg.object_id)
        else:
            cfg.object_id = [cfg.object_id]

    # iterate objects ids
    for object_idx in cfg.object_id:
        cols = []
        for cam_id in cfg.cameras:
            row = []
            for light_id in cfg.lights:
                image = rene.get(object_idx, light_id, cam_id, "image")

                # crop image:
                crop_x, crop_y, crop_w, crop_h = cfg.crop
                if crop_x > 0:
                    if cfg.crop_type == "tl":
                        image = image[
                            crop_y : crop_y + crop_h, crop_x : crop_x + crop_w
                        ]
                    elif cfg.crop_type == "center":
                        image = image[
                            crop_y - crop_h // 2 : crop_y + crop_h // 2,
                            crop_x - crop_w // 2 : crop_x + crop_w // 2,
                        ]

                # add image borders
                image = cv2.copyMakeBorder(
                    image,
                    top=cfg.borders,
                    bottom=cfg.borders,
                    left=cfg.borders,
                    right=cfg.borders,
                    borderType=cv2.BORDER_CONSTANT,
                    value=cfg.borders_color,
                )

                row.append(image)
            cols.append(row)

        # swap rows and cols
        if transpose:
            cols = list(map(list, zip(*cols)))

        # stack cols/rows in a single mosaic
        cols = [np.hstack(row) for row in cols]
        cols = np.vstack(cols)

        # remove outer borders if needed (copyMakeBorder adds borders to the whole image)
        if not cfg.outer_border:
            cols = cols[
                cfg.borders : -cfg.borders,
                cfg.borders : -cfg.borders,
            ]

        # debug show
        cv2.imshow("image", cv2.cvtColor(cols, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)

        # write image
        output_filename = os.path.join(output_folder, f"object_{object_idx}.png")
        cv2.imwrite(
            output_filename,
            cv2.cvtColor(cols, cv2.COLOR_RGB2BGR),
        )
        rich.print("Image saved to", output_filename)


if __name__ == "__main__":
    typer.run(name)
