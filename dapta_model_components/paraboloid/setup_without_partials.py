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

    # initalise setup_data keys - none for paraboloid
    response = {}

    # set default inputs
    if inputs:
        for input_key, input_value in inputs.items():
            if input_value == "default":
                try:
                    inputs[input_key] = params[input_key]
                except Exception as e:
                    print(f"Could not find {input_key} in the input parameters.")
        response["inputs"] = inputs
        print(inputs)

    # initialise outputs - required for OpenMDAO
    if outputs:
        for output_key, output_value in outputs.items():
            if output_value == "default":
                try:
                    outputs[output_key] = params[output_key]
                except Exception as e:
                    print(f"Could not find {output_key} in the input parameters.")
        response["outputs"] = outputs
        print(outputs)

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."
    print(message)
    response["message"] = message

    return response
