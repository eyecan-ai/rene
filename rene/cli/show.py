import typing as t
from pathlib import Path

import cv2
import numpy as np
from pipelime.sequences import Sample
from pipelime.stages import SampleStage
from pydantic import Field

import rene.cli as c


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


@c.command(title="show")
def show(
    input_folder: Path = c.Field(..., alias="i", description="ReNé parent folder"),
):
    """
    Show the content of the dataset, with the possibility to select the scene, light and viewpoint
    """

    from functools import partial

    import matplotlib.pyplot as plt
    import rich
    from matplotlib.widgets import Button
    from pipelime.sequences import SamplesSequence
    from rich.progress import track

    from rene.utils import DATA_KEYS

    ########################
    # DATASET LAZY LOADING #
    ########################

    res = ResizeStage(target_size=(1440 // 2, 1080 // 2))  # type: ignore
    res_thumb = ResizeStage(target_size=(1440 // 10, 1080 // 10))  # type: ignore

    # Loop over the subfolders of the input folder
    subs = [
        x
        for x in list(sorted(input_folder.iterdir()))
        if x.name.split("_")[0] in DATA_KEYS and x.is_dir()
    ]

    rene = {}
    rene_thumb = {}
    for sub in track(subs, description="Lazy Loading Dataset..."):
        # Get the list of lightsets
        lsets = [x for x in list(sorted(sub.iterdir()))]
        name = sub.name.split("_")[0]

        # Create the thumbnails
        uf_thumb = SamplesSequence.from_underfolder(lsets[0]).map(res_thumb)
        rene_thumb[name] = uf_thumb[0]["image"]()

        # Create structure to manage the data
        rene[name] = [None] * (int(lsets[-1].name.removeprefix("lset")) + 1)
        for lset in lsets:
            uf = SamplesSequence.from_underfolder(lset).map(res)
            rene[name][int(lset.name.removeprefix("lset"))] = uf

    ##########################
    # FIGURE INITIIALIZATION #
    ##########################

    # Initialize data and state
    q_data = {"name": "apple", "light": 0, "pose": 0}
    s_data = {"p": None, "l": None, "t": ""}
    init_rene = rene[q_data["name"]]

    # Create the figure
    rich.print("Creating the figure...")
    fig = plt.figure()
    plt.get_current_fig_manager().set_window_title("")
    fig.suptitle(
        "ReNé Dataset Viewer",
        color="#363636",
        fontsize=20,
        fontweight="bold",
        va="top",
        ha="center",
    )

    # Plot poses and lights
    ax1 = fig.add_subplot(121, projection="3d", computed_zorder=False)

    ax1.set_xlim3d(-0.4, 0.4)
    ax1.set_ylim3d(-0.4, 0.4)
    ax1.set_zlim3d(0, 0.5)
    ax1.set_title("click on a viewpoint or a lightset", y=0.8, fontsize=12)

    ax1.scatter([0], [0], [0], c="#AC0400", marker="o", s=100)  # scatter object
    scatter_poses = ax1.scatter(
        [init_rene[0][i]["pose"]()[0, 3] for i in range(len(init_rene[0]))],
        [init_rene[0][i]["pose"]()[1, 3] for i in range(len(init_rene[0]))],
        [init_rene[0][i]["pose"]()[2, 3] for i in range(len(init_rene[0]))],
        color="#FF75FF",
    )
    scatter_poses.set_picker(True)

    scatter_light = ax1.scatter(
        [init_rene[i][0]["light"]()[0, 3] for i in range(len(init_rene))],
        [init_rene[i][0]["light"]()[1, 3] for i in range(len(init_rene))],
        [init_rene[i][0]["light"]()[2, 3] for i in range(len(init_rene))],
        color="#00D1B2",
    )
    scatter_light.set_picker(True)
    ax1.axis("off")

    # Create the buttons
    btns = {}
    for i, k in enumerate(list(rene_thumb.keys())):
        n = len(rene_thumb.keys())
        btns[k] = {}
        btns[k]["ax"] = fig.add_axes([1 / n * i, 1 / n, 1 / n, 1 / n])
        btns[k]["ax"].set_title("click on a scene") if i == n // 2 else None
        btns[k]["obj"] = Button(btns[k]["ax"], "", image=rene_thumb[k])

    # Create the image plot
    ax2 = fig.add_subplot(122)
    ax2.axis("off")

    #######################
    # CALLBACK DEFINITION #
    #######################

    def on_click(name, e):
        # Update the data after click event
        if e is None or hasattr(e, "artist"):
            # Update camera pose
            if e is None or e.artist == scatter_poses:
                q_data["pose"] = e.ind[0] if e is not None else q_data["pose"]
                # Add point to the selected pose
                ps = rene[q_data["name"]][q_data["light"]][q_data["pose"]]["pose"]()
                s_data["p"].remove() if s_data["p"] else None
                s_data["p"] = ax1.scatter(
                    [ps[0, 3]], [ps[1, 3]], [ps[2, 3]], s=40, c="#48C774"
                )
            # Update light pose
            if e is None or e.artist == scatter_light:
                q_data["light"] = e.ind[0] if e is not None else q_data["light"]
                # Add point to the selected light
                lt = rene[q_data["name"]][q_data["light"]][q_data["pose"]]["light"]()
                s_data["l"].remove() if s_data["l"] else None
                s_data["l"] = ax1.scatter(
                    [lt[0, 3]], [lt[1, 3]], [lt[2, 3]], s=40, c="#FFDD57"
                )

        if e is None or not hasattr(e, "artist"):
            q_data["name"] = name
            # Add the border to the selected thumbnail
            for side in ["top", "bottom", "left", "right"]:
                for name, btn in btns.items():
                    btn["ax"].spines[side].set_linewidth(0.5)
                    btn["ax"].spines[side].set_color("black")
                    if name == q_data["name"]:
                        btn["ax"].spines[side].set_linewidth(2.5)
                        btn["ax"].spines[side].set_color("#AC0400")

        # Update the image accordingly
        im = rene[q_data["name"]][q_data["light"]][q_data["pose"]]["image"]()
        s_data["t"].remove() if s_data["t"] else None

        ## If the image is all black, add a text to indicate that it is a test image
        if np.all(im == 0):
            s_data["t"] = ax2.text(
                x=im.shape[1] // 2,
                y=im.shape[0] // 2,
                s="Test image!",
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                c="w",
            )
            ax2.imshow(im)
        else:
            s_data["t"] = ""
            ax2.imshow(im)

        fig.canvas.draw()

    #######################
    # CALLBACK CONNECTION #
    #######################

    # Connect the callback function to the figure and the buttons
    fig.canvas.mpl_connect("pick_event", partial(on_click, q_data["name"]))
    [btns[k]["obj"].on_clicked(partial(on_click, k)) for k in list(rene_thumb.keys())]

    rich.print("Done creating the figure!")

    ###################
    # FIGURE SPAWNING #
    ###################

    # We run once the callback function to initialize the figure
    on_click(q_data["name"], None)
    plt.show()
