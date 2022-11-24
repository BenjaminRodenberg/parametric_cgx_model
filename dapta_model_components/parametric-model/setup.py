from datetime import datetime
from pathlib import Path


def setup(
    inputs: dict = None,
    outputs: dict = None,
    partials: dict = None,
    params: dict = None,
    run_folder: Path = None,
    inputs_folder: Path = None,
):
    """Editable setup function."""

    # initalise setup_data keys
    response = {"output_files.cgx_file": None}

    # set default inputs
    if inputs:
        for input_key, input_value in inputs.items():
            if input_value == "default":
                try:
                    inputs[input_key] = params[input_key]
                except Exception as e:
                    print(f"Could not find {input_key} in the input parameters.")
        response["inputs"] = inputs

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."
    print(message)
    response["message"] = message

    return response
