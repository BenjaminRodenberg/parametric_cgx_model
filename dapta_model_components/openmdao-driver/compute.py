from datetime import datetime
from pathlib import Path
import traceback
from contextlib import redirect_stdout
import numpy as np
import openmdao.api as om

from component_api2 import call_compute
from om_component import OMexplicitComp  # type: ignore


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

    print("OpenMDAO problem setup started.")

    workflow = setup_data["workflow"]
    all_connections = setup_data["all_connections"]

    # 1) define the simulation components
    prob = om.Problem()
    for component in workflow:
        prob.model.add_subsystem(
            component,
            OMexplicitComp(name=component, run_number=0),
        )

    # 2) define the component connections
    for connection in all_connections:
        if connection["type"] == "design":
            prob.model.connect(
                connection["origin"]
                + "."
                + connection["name_origin"].replace(".", "-"),
                connection["target"]
                + "."
                + connection["name_target"].replace(".", "-"),
            )

    if setup_data["driver"]["type"] == "optimisation":
        # 3) setup the optimisation driver options
        prob.driver = om.ScipyOptimizeDriver()
        prob.driver.options["optimizer"] = setup_data["optimizer"]
        prob.driver.options["maxiter"] = setup_data["max_iter"]
        prob.driver.options["tol"] = setup_data["tol"]
        prob.driver.opt_settings["disp"] = setup_data["disp"]
        prob.driver.options["debug_print"] = setup_data["debug_print"]

        if "approx_totals" in setup_data and setup_data["approx_totals"]:
            # ensure FD gradients are used
            prob.model.approx_totals(
                method="fd", step=0.0001, form=None, step_calc=None
            )

    elif setup_data["driver"]["type"] == "doe":
        # 3) alternative: setup a design of experiments
        prob.driver = om.DOEDriver(
            om.UniformGenerator(num_samples=setup_data["driver"]["samples"])
        )

    # 4) add design variables
    for var in setup_data["input_variables"]:
        comp = var["component"]
        lower = var["lower"]
        upper = var["upper"]
        prob.model.add_design_var(
            f"{comp}.{var['name'].replace('.', '-')}",
            lower=lower,
            upper=upper,
        )

    # 5) add an objective and constraints
    for var in setup_data["output_variables"]:
        comp = var["component"]
        name = f"{comp}.{var['name'].replace('.', '-')}"

        # set scaling from parameter input file
        if "scaler" in var:
            scaler = var["scaler"]
        else:
            scaler = None
        if "adder" in [var]:
            adder = var["adder"]
        else:
            adder = None

        if var["type"] == "objective":
            prob.model.add_objective(name, scaler=scaler, adder=adder)
        elif var["type"] == "constraint":
            if "lower" in var:
                lower = var["lower"]
            else:
                lower = None
            if "upper" in var:
                upper = var["upper"]
            else:
                upper = None
            prob.model.add_constraint(
                name, lower=lower, upper=upper, scaler=scaler, adder=adder
            )

    prob.setup()  # required to generate the n2 diagram
    print("OpenMDAO problem setup completed.")

    if "visualise" in setup_data and "n2_diagram" in setup_data["visualise"]:
        # save n2 diagram in html format
        om.n2(
            prob,
            outfile=str(run_folder / "n2.html"),
            show_browser=False,
        )

    if setup_data["driver"]["type"] == "optimisation":
        dict_out = run_optimisation(prob, setup_data, run_folder)

    # elif setup_data["driver"]["type"] == "check_partials":
    #     dict_out = run_check_partials(prob, setup_data)

    # elif setup_data["driver"]["type"] == "check_totals":
    #     dict_out = run_check_totals(prob, setup_data)

    # elif setup_data["driver"]["type"] == "doe":
    #     dict_out = run_doe(prob, setup_data)

    # elif setup_data["driver"]["type"] == "post":
    #     dict_out = run_post(prob, setup_data)

    else:
        raise ValueError(
            f"driver {setup_data['driver']['type']} is not a valid component driver type."
        )

    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: OpenMDAO compute completed."
    print(message)

    return {"message": message, "outputs": dict_out["outputs"]}


def run_optimisation(prob, setup_data, run_folder):

    # 6) add a data recorder to the optimisation problem
    r_name = str(
        run_folder
        / (
            "om_problem_recorder_"
            + datetime.now().strftime("%Y%m%d-%H%M%S")
            + ".sqlite"
        )
    )
    r = om.SqliteRecorder(r_name)
    prob.driver.add_recorder(r)
    prob.driver.recording_options["record_derivatives"] = True

    # setup the problem again
    prob.setup()

    if "visualise" in setup_data and "scaling_report" in setup_data["visualise"]:
        # NOTE: running the model can generate large large amounts of stored data in orchestrator, which
        # can cause prob.setup() to fail if it is called again, so only execute
        # prob.run_model() after all setup has been completed
        with open(run_folder / "scaling_report.log", "w") as f:
            with redirect_stdout(f):
                prob.run_model()
                prob.driver.scaling_report(
                    outfile=str(run_folder / "driver_scaling_report.html"),
                    title=None,
                    show_browser=False,
                    jac=True,
                )

    # 7) execute the optimisation
    try:
        with open(run_folder / "run_driver.log", "w") as f:
            with redirect_stdout(f):
                prob.run_driver()
    except Exception as e:
        print(f"run driver exited with error: {e}")
        tb = traceback.format_exc()
        raise ValueError("OpenMDAO Optimisation error: " + tb)

    opt_output = {}
    # print("Completed model optimisation - solution is: \n inputs= (")
    for var in setup_data["input_variables"]:
        comp = var["component"]
        name = var["name"]
        # print(
        #     f"{comp}.{name}: "
        #     + str(prob.get_val(f"{comp}.{name.replace('.', '-')}"))
        #     + " "
        # )
        opt_output[f"{comp}.{name}"] = prob.get_val(
            f"{comp}.{name.replace('.', '-')}"
        ).tolist()
    # print("), \n outputs = (")
    for var in setup_data["output_variables"]:
        comp = var["component"]
        name = var["name"]
        # print(
        #     f"{comp}.{name}: "
        #     + str(prob.get_val(f"{comp}.{name.replace('.', '-')}"))
        #     + " "
        # )
        opt_output[f"{comp}.{name}"] = prob.get_val(
            f"{comp}.{name.replace('.', '-')}"
        ).tolist()
    # print(")")

    print(opt_output)

    return {"outputs": opt_output}
