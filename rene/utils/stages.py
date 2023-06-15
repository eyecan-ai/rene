import typing as t

import cv2
import numpy as np
from pipelime.sequences import Sample
from pipelime.stages import SampleStage
from pydantic import Field


class ResizeStage(SampleStage, title="resize"):
    """Resize an image and a camera to a target size"""

    target_size: t.Tuple[int, int] = Field(..., description="The target size.")
    images_keys: t.Sequence[str] = Field(["image"], description="Key of ims to resize.")
    camera_key: t.Optional[str] = Field("camera", description="Key cam to resize")

    def __call__(self, s: Sample) -> Sample:
        # resizing the image
        for key in self.images_keys:
            image: np.ndarray = s[key]()  # type: ignore
            new_image = cv2.resize(
                image,
                dsize=(self.target_size[0], self.target_size[1]),
                interpolation=cv2.INTER_CUBIC,
            )

            s = s.set_value(key, new_image)

        if self.camera_key is not None:
            camera: dict[str, dict] = s[self.camera_key]()  # type: ignore
            src_size = camera["intrinsics"]["image_size"]

            if src_size != self.target_size:
                cm = np.asarray(camera["intrinsics"]["camera_matrix"])
                cm_new = np.eye(3)
                cm_new[0, 0] = cm[0, 0] * (self.target_size[1] / src_size[1])
                cm_new[1, 1] = cm[1, 1] * (self.target_size[0] / src_size[0])
                cm_new[0, 2] = cm[0, 2] * (self.target_size[1] / src_size[1])
                cm_new[1, 2] = cm[1, 2] * (self.target_size[0] / src_size[0])
                camera["intrinsics"]["camera_matrix"] = cm_new.tolist()
                camera["intrinsics"]["image_size"] = self.target_size

                s = s.set_value(self.camera_key, camera)

        return s
