import typing as t
from pathlib import Path

from pipelime.sequences import SamplesSequence
from rich.progress import track


def lazy_load(input_folder: Path) -> t.MutableMapping[str, t.List[SamplesSequence]]:
    """
    Lazy load the entire dataset
    """
    # Loop over the subfolders of the input folder
    scenes = [x for x in list(sorted(input_folder.iterdir()))]

    # We lazy load the entire dataset
    rene = {}
    for scene in track(scenes, description="Lazy Loading Dataset..."):
        lsets = [x for x in list(sorted(scene.iterdir()))]
        rene[scene.name] = [SamplesSequence.from_underfolder(lset) for lset in lsets]

    return rene
