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


    # set default inputs
    if inputs:
        for input_key, input_value in inputs.items():
            if input_value == "default":
                tree = input_key.split(".")
                try:
                    inputs[input_key] = getFromDict(params, tree)
                except Exception as e:
                    print(f"Could not find {input_key} in the input parameters.")

    # initiate output values
    if outputs:
        for output in outputs:
            outputs[output] = None

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."

    return {"message": message, "inputs": inputs, "outputs": outputs}


def getFromDict(dataDict: dict, mapList: list):
    """Traverse a dictionary and get value by providing a list of keys."""
    return reduce(getitem, mapList, dataDict)
