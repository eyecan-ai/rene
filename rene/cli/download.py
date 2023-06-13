import typing as t
from pathlib import Path

import rene.cli as c


@c.command(title="download")
def download(
    output_folder: Path = c.Field(..., alias="o", description="Folder with ReNé zips"),
    scene_name: t.Union[str, t.List[str]] = c.Field(
        [],
        alias="s",
        description="Specify this argument to download only a subset of the scenes",
    ),
):
    """
    Download a scene from the dataset
    """
    import wget
    from rich import print

    from rene.utils import DATA_URLS

    # Literals for Google Drive
    GPREFIX = "https://docs.google.com/uc?export=download&confirm=t&id="
    GSTART = "https://drive.google.com/file/d/"
    GEND = "/view?usp=drive_link"

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
            id = (DATA_URLS[n].split(GSTART))[1].split(GEND)[0]
            out = wget.download(f"{GPREFIX}{id}", str(output_folder / f"{n}.zip"))
            print("\n")
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
    print("\n")
    print(f"[bold]Downloaded {len(downloaded)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Existing {len(existing)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Failed {len(failed)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
    print(f"[bold]Not Found {len(not_found)}/{len(ns)} scenes[/bold]")
