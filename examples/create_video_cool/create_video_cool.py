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
import albumentations as A


def create_video(
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

    # T
    T = A.Compose(
        [
            A.SmallestMaxSize(max_size=512),
            A.PadIfNeeded(
                min_height=None,
                min_width=None,
                pad_height_divisor=2,
                pad_width_divisor=2,
                border_mode=cv2.BORDER_REFLECT,
            ),
        ]
    )

    # Rene Browser
    rene = ReNeDataset(input_folder, reorder_camera_indices=False)

    object_indices = list(range(rene.num_objects()))

    ordered_camera_indices = rene.CAMERA_ORDERED_INDICES
    middle_camera_indices_size = len(ordered_camera_indices) // 2

    light_indices = list(range(rene.num_lights()))

    batches = []
    for index, object_id in enumerate(object_indices):

        current_orderer_camera_indices = ordered_camera_indices.copy()
        current_light_indices = light_indices.copy()

        if index % 2 == 0:
            # reverse
            current_orderer_camera_indices = current_orderer_camera_indices[::-1]
            current_light_indices = current_light_indices[::-1]

        batches.append(
            {
                "object_ids": [object_id] * middle_camera_indices_size,
                "cam_ids": current_orderer_camera_indices[:middle_camera_indices_size],
                "light_ids": [0] * middle_camera_indices_size,
            }
        )
        batches.append(
            {
                "object_ids": [object_id] * len(current_light_indices),
                "cam_ids": [current_orderer_camera_indices[middle_camera_indices_size]]
                * len(current_light_indices),
                "light_ids": current_light_indices,
            }
        )
        batches.append(
            {
                "object_ids": [object_id] * middle_camera_indices_size,
                "cam_ids": current_orderer_camera_indices[middle_camera_indices_size:],
                "light_ids": [current_light_indices[-1]] * middle_camera_indices_size,
            }
        )

    save_counter = 0

    for batch in batches:
        object_ids = batch["object_ids"]
        cam_ids = batch["cam_ids"]
        light_ids = batch["light_ids"]
        print(object_ids, cam_ids, light_ids)

        for object_indices, cam_id, light_id in zip(object_ids, cam_ids, light_ids):
            image = rene.get(object_indices, light_id, cam_id, "image")
            image = T(image=image)["image"]

            # draw labels on image bottom right
            image = cv2.putText(
                image,
                f"Object: {object_indices}",
                (image.shape[1] - 200, image.shape[0] - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
            image = cv2.putText(
                image,
                f"Camera: {cam_id}",
                (image.shape[1] - 200, image.shape[0] - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
            image = cv2.putText(
                image,
                f"Light: {light_id}",
                (image.shape[1] - 200, image.shape[0] - 0),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )

            if debug:
                print("Image Shape", image.shape)
                # debug show
                cv2.imshow("image", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                cv2.waitKey(0)

            # save image
            save_path = output_folder / f"{save_counter:04d}_image.png"
            cv2.imwrite(str(save_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            print(f"Saved image to {save_path}")
            save_counter += 1


if __name__ == "__main__":
    typer.run(create_video)
