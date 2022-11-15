from functools import reduce
from operator import getitem
from datetime import datetime
import traceback


def setup(
    inputs: dict = None,
    outputs: dict = None,
    partials: dict = None,
    params: dict = None,
):
    """Editable setup function."""

    # declare default parameter inputs - overriden by connection data if available
    param_input_file = params["param_input_files.cgx_file"]

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."

    return {"message": message, "param_input_files.cgx_file": param_input_file}


def getFromDict(dataDict: dict, mapList: list):
    """Traverse a dictionary and get value by providing a list of keys."""
    return reduce(getitem, mapList, dataDict)
