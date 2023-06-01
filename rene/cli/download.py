import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="download")
def download_scene(
    output_folder: Path = c.Field(
        ...,
        alias="o",
        description="The folder where to download the scenes",
        piper_port=c.OUT,
    ),
    scene_name: t.Union[str, t.List[str]] = c.Field(
        [],
        alias="s",
        description="The name of the scene to download, if None all scenes will be downloaded",
        piper_port=c.IN,
    ),
):
    """
    Download a scene from the dataset
    """
    import gdown
    from rich import print

    from rene.utils import DATA_URLS

    output_folder.mkdir(exist_ok=True, parents=True)

    # Here we make sure that scene_names is a list, if is empty we download all scenes
    ns = scene_name if isinstance(scene_name, t.List) else [scene_name]
    ns = list(DATA_URLS.keys()) if len(ns) == 0 else ns

    downloaded = []
    existing = []
    failed = []
    not_found = []
    for i, n in enumerate(ns):
        print(f"[bold][green]{n.capitalize()}[/green] scene ({i+1}/{len(ns)})[/bold]")

        if n not in DATA_URLS:
            print(f"[/bold][red]Scene {n} not found[/red][/bold]")
            not_found.append(n)
            continue

        if (output_folder / f"{n}.zip").exists():
            print(f"[bold][yellow]Scene {n} already downloaded[/yellow][/bold]")
            existing.append(n)
            continue

        try:
            out = gdown.download(
                id=DATA_URLS[n], output=str(output_folder / f"{n}.zip")
            )
            if out is None:
                raise Exception()
        except Exception as e:
            print(f"[bold][red]Error downloading {n} scene[/red][bold]")
            failed.append(n)
            continue
        else:
            print(f"[green]Scene {n} downloaded[/green]")
            downloaded.append(n)

    # Summary of downloaded scenes
    print(f"[bold]Downloaded {len(downloaded)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Existing {len(existing)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Failed {len(failed)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
