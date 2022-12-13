from datetime import datetime
from pathlib import Path


def setup(
    inputs: dict = None,
    outputs: dict = None,
    partials: dict = None,
    parameters: dict = None,
):
    """Editable setup function."""

    # declare default parameter inputs - overriden by connection data if available
    if "files.analysis_output_file" in parameters:
        inputs["implicit"]["files.analysis_output_file"] = parameters[
            "files.analysis_output_file"
        ]
    else:
        inputs["implicit"]["files.analysis_output_file"] = "default"

    if "files.mesh_file" in parameters:
        inputs["implicit"]["files.mesh_file"] = parameters["files.mesh_file"]
    else:
        inputs["implicit"]["files.mesh_file"] = "default"

    if "files.nodeset_file" in parameters:
        inputs["implicit"]["files.nodeset_file"] = parameters["files.nodeset_file"]
    else:
        inputs["implicit"]["files.nodeset_file"] = "default"

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Setup completed."

    return {"message": message, "inputs": inputs}
