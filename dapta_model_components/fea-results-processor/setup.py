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
    if "param_input_files.analysis_output_file" in params:
        analysis_output_file = params["param_input_files.analysis_output_file"]
    else:
        analysis_output_file = "default"

    if "param_input_files.mesh_file" in params:
        mesh_file = params["param_input_files.mesh_file"]
    else:
        mesh_file = "default"

    if "param_input_files.nodeset_file" in params:
        nodeset_file = params["param_input_files.nodeset_file"]
    else:
        nodeset_file = "default"

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."

    return {
        "message": message,
        "param_input_files.analysis_output_file": analysis_output_file,
        "param_input_files.mesh_file": mesh_file,
        "param_input_files.nodeset_file": nodeset_file,
    }
