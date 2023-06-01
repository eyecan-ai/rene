"""Top-level package for rene dataset."""

__author__ = "eyecan.ai"
__email__ = "info@eyecan.ai"
__version__ = "0.0.1"


def app():
    """This is the entry point of eyecan.ai rene dataset!"""
    from pipelime.cli import PipelimeApp

    app = PipelimeApp("rene.cli", app_version=__version__)
    app()
