from datetime import datetime
from pathlib import Path
from component_api2 import call_compute

import matplotlib.pyplot as plt


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

    study_results = []
    parameter_values = range(0, 50, 5)

    for rotation in parameter_values:

        # update rotation input variable
        component_inputs["calculix-fea"]["fibre_rotation_angle.ORI_0.1"] = float(
            rotation
        )

        (msg, output) = run_workflow(workflow, component_inputs)

        if not "outputs" in output:
            raise ValueError("Cannot find 'output' dictionary in run_workflow output.")

        study_results.append(output["outputs"])

    plot_data = _plot_study_results(
        study_results,
        x=parameter_values,
        y=["Uz", "Ry"],
        saveas=str(run_folder / "results_plot"),
    )
    print(plot_data)
    print("Parametric study completed.")

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: {msg}"
    print(message)

    return {"message": message}


def run_workflow(workflow, component_inputs):
    """Execute the workflow components in the same way the Orchestrator would do."""

    msgs = ""
    for component in workflow:
        indict = {
            "component": component,
            "get_grads": False,
            "get_outputs": True,
        }
        if component in component_inputs:
            indict["inputs"] = component_inputs[component]
        (msg, output) = call_compute(indict)
        print(msg)
        msgs += msg + "\n"

    return (msgs, output)


def _plot_study_results(
    output: list,  # list of dictionaries
    x: list,  # x-values
    y: list,  # key of y-values
    xlabel="ply rotation angle (deg)",
    ylabel="displacements (m) or rotation (rad)",
    saveas=None,
):

    y_series = []
    for result in output:
        if len(y) == 1 and isinstance(result[y[0]], list):
            if len(output) > 1:
                y_series.append(result[y[0]])
            else:
                y_series = result[y[0]]
        else:
            y_series.append([result[label] for label in y])

    lineObjects = plt.plot(x, y_series)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(iter(lineObjects), y)

    if saveas:
        plt.savefig(saveas + ".png")
        plt.savefig(saveas + ".pdf")

    plt.show()

    return {
        "x_label": "rotation_angles",
        "x_values": x,
        "y_labels": y,
        "y_values": y_series,
    }
