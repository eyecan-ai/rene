"""
Here are the console configuration
"""
from rich.traceback import install

install(show_locals=False)

"""
Below are imports used for zero boilerplate
"""

from pipelime.cli import run
from pipelime.piper import PiperPortType, command, self_
from pipelime.utils.pydantic_types import NewPath
from pydantic import Field

IN = PiperPortType.INPUT
OUT = PiperPortType.OUTPUT
PARAM = PiperPortType.PARAMETER

"""
Above are imports used to let the entry point know what to import
Import other functions decorated with @command if you'd like
to see them when calling "nsext list" from command line
They should go here below to avoid circular imports
"""

from rene.cli.benchmark import check_format, convert_scene
from rene.cli.copy_calibration import copy_calib, fix_calib_cam
from rene.cli.download import download
from rene.cli.filter import filter_calibration
from rene.cli.png_to_jpg import convert
from rene.cli.show import show
from rene.cli.split import blackout
from rene.cli.zipp import compress, extract
