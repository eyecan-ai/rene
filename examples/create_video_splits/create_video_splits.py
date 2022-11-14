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


def draw_boxed_label(
    image: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font: int = cv2.FONT_HERSHEY_SIMPLEX,
    font_size: float = 0.5,
    font_color: Tuple[int, int, int] = (255, 255, 255),
    background_color: Tuple[int, int, int] = (0, 0, 0),
    thickness: int = 3,
    line_type: int = cv2.LINE_AA,
    bottom_left_origin: bool = False,
    padding: Tuple[int, int] = (50, 50),
) -> np.ndarray:
    """
    Put text on image with colored box as background.

    Args:
        image (np.ndarray): Image to put text on.
        text (str): Text to put on image.
        position (Tuple[int, int]): Position of text.
        font (int, optional): Font to use. Defaults to cv2.FONT_HERSHEY_SIMPLEX.
        font_size (float, optional): Font size. Defaults to 0.5.
        font_color (Tuple[int, int, int], optional): Font color. Defaults to (255, 255, 255).
        background_color (Tuple[int, int, int], optional): Background color. Defaults to (0, 0, 0).
        thickness (int, optional): Thickness of text. Defaults to 1.
        line_type (int, optional): Line type. Defaults to cv2.LINE_AA.
        bottom_left_origin (bool, optional): Bottom left origin. Defaults to False.
        padding (Tuple[int, int], optional): Padding of text. Defaults to (10, 10).

    Returns:
        np.ndarray: Image with text.
    """
    # get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_size, thickness
    )

    # draw background
    cv2.rectangle(
        image,
        position,
        (position[0] + text_width + padding[0], position[1] - text_height - padding[1]),
        background_color,
        cv2.FILLED,
    )

    # draw text
    cv2.putText(
        image,
        text,
        (position[0] + padding[0] // 2, position[1] - padding[1] // 2),
        font,
        font_size,
        font_color,
        thickness,
        line_type,
        bottom_left_origin,
    )

    return image


class Config(pydantic.BaseModel):
    object_ids: Union[int, List[int]]
    easy_camera_indices: list = [15]
    hard_light_indices: list = [2, 21, 34]
    hard_repeats: int = 6
    default_camera_index: int = 0


def create_video_with_steps(
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
        help="Resize the image [smallest max size]",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Debug mode",
    ),
):
    # Load yaml cfg fle
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    cfg = Config(**cfg)

    # Output folder
    output_folder = Path(output_folder)
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

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

    # Rene Browser
    rene = ReNeDataset(input_folder, reorder_camera_indices=False)

    if isinstance(cfg.object_ids, int):
        if cfg.object_ids == -1:
            object_indices = list(range(rene.num_objects()))
        else:
            object_indices = [cfg.object_ids]
    else:
        object_indices = cfg.object_ids

    camera_indices = rene.CAMERA_ORDERED_INDICES
    light_indices = list(range(rene.num_lights()))

    # remove cfg.hard_light_indices from light_indices
    # light_indices = [i for i in light_indices if i not in cfg.hard_light_indices]
    # light_indices += cfg.hard_light_indices

    default_camera_index = light_indices[cfg.default_camera_index]

    bunches = []
    for object_index in object_indices:
        for camera_index in camera_indices:
            if camera_index in cfg.easy_camera_indices:
                for light_index in light_indices:
                    hard_sample = (
                        light_index in cfg.hard_light_indices
                        and camera_index in cfg.easy_camera_indices
                    )
                    repeats = cfg.hard_repeats if hard_sample else 1
                    for _ in range(repeats):
                        bunches.append((object_index, camera_index, light_index))
            else:
                bunches.append((object_index, camera_index, default_camera_index))

    save_counter = 0
    for bunch in bunches:
        object_id, cam_id, light_id = bunch

        image = rene.get(object_id, light_id, cam_id, "image")

        label = "Train"
        colors = {"text": (22, 22, 22), "background": (250, 250, 250)}
        if cam_id in cfg.easy_camera_indices and not light_id in cfg.hard_light_indices:
            label = "Easy Test"
            colors = {"text": (250, 250, 250), "background": (38, 166, 154)}
        elif cam_id in cfg.easy_camera_indices and light_id in cfg.hard_light_indices:
            label = "Hard Test"
            colors = {"text": (250, 250, 250), "background": (236, 64, 122)}

        # draw label with background color big as text in the bottom left corner
        draw_boxed_label(
            image,
            label,
            (10, image.shape[0] - 10),
            font_size=4.5,
            font_color=colors["text"],
            background_color=colors["background"],
        )

        if debug:
            cv2.imshow("image", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            cv2.waitKey(0)

        # transform
        image = T(image=image)["image"]

        # Save image
        save_path = output_folder / f"{save_counter:05d}.png"
        cv2.imwrite(str(save_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        print(f"Saved {save_path}")
        save_counter += 1


if __name__ == "__main__":
    typer.run(create_video_with_steps)
