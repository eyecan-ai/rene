from pathlib import Path

import rene.cli as c


@c.command(title="show")
def show(
    input_folder: Path = c.Field(..., alias="i", description="ReNé parent folder"),
):
    """
    Show the content of the dataset, with the possibility to select the scene, light and viewpoint
    """

    from functools import partial

    import matplotlib.pyplot as plt
    import numpy as np
    import rich
    from matplotlib.widgets import Button

    from rene.utils.loaders import ReneDataset

    ########################
    # DATASET LAZY LOADING #
    ########################

    rene = ReneDataset(
        input_folder=input_folder,
        image_max_size=540,
        thumb_max_size=144,
    )

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

    # Create the image plot
    ax2 = fig.add_subplot(122)
    ax2.axis("off")

    # Create the buttons
    btns = {}
    fig.text(0.5, 0.065, "click on a scene", ha="center", fontsize=12)
    n = len(rene.keys())
    shift = 0.5 - (n // 2) / 21 if n % 2 == 0 else 0.5 - (n // 2) / (21 - 1)
    for i, k in enumerate(list(rene.keys())):
        btns[k] = {}
        btns[k]["ax"] = fig.add_axes([1 / 21 * i + shift, 0.01, 1 / 21, 1 / 21])
        btns[k]["obj"] = Button(btns[k]["ax"], "", image=rene[k][0][0]["thumb"]())

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
    [btns[k]["obj"].on_clicked(partial(on_click, k)) for k in list(rene.keys())]

    rich.print("Done creating the figure!")

    ###################
    # FIGURE SPAWNING #
    ###################

    # We run once the callback function to initialize the figure
    on_click(q_data["name"], None)
    plt.show()
