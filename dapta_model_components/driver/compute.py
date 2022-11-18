from datetime import datetime
from pathlib import Path
from component_api2 import call_compute


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

    """Editable compute function."""

    workflow = setup_data["workflow"]
    component_inputs = setup_data["component_inputs"]  # note: params not accessible
    msg = run_workflow(workflow, component_inputs)

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: {msg}"
    print(message)

    return {"message": message}


def run_workflow(workflow, component_inputs):
    """Execute the workflow components in the same way the Orchestrator would do."""

    msgs = ""
    for component in workflow:
        (msg, _) = call_compute(
            {
                "component": component,
                "inputs": component_inputs[component],
                "get_grads": False,
                "get_outputs": True,
            }
        )
        print(msg)
        msgs += msg + "\n"

    return msg
