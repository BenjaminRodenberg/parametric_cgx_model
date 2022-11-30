from datetime import datetime
from pathlib import Path


def compute(
    setup_data: dict = None,
    params: dict = None,
    inputs: dict = None,
    outputs: dict = None,
    partials: dict = None,
    options: dict = None,
    run_folder: Path = None,
    inputs_folder: Path = None,
):

    """
    Evaluates the equation f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3.
    Minimum at: x = 6.6667; y = -7.3333
    """

    if isinstance(inputs["x"], list):
        x = inputs["x"][0]
    elif isinstance(inputs["x"], (float, int)):
        x = float(inputs["x"])

    if isinstance(inputs["y"], list):
        y = inputs["y"][0]
    elif isinstance(inputs["y"], (float, int)):
        y = float(inputs["y"])

    print("inputs: ", x, y)
    print("options: ", options)

    resp = {}

    outputs["f_xy"] = [(x - 3.0) ** 2 + x * y + (y + 4.0) ** 2 - 3.0]
    resp["outputs"] = outputs

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Compute parabolla f[x:{str(x)},y:{str(y)}] = {str(outputs['f_xy'])} with options: {str(options)}"
    print(message)
    resp["message"] = message

    return resp
