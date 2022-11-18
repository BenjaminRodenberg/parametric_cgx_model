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

    # declare default parameter inputs - overriden by connection data if available
    if "param_input_files.cgx_file" in params:
        param_input_file = params["param_input_files.cgx_file"]
    else:
        param_input_file = "default"

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."

    return {
        "message": message,
        "param_input_files.cgx_file": param_input_file,
        "output_files.analysis_output_file": "default",
        "output_files.mesh_file": "default",
        "output_files.nodeset_file": "default",
    }
