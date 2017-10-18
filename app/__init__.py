from .cli import cli
from .gui import gui


def run_app(ars=[]):
    if len(ars) >= 2:
        cli()
    else:
        gui()
