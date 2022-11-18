import shutil
from datetime import datetime
from pathlib import Path
from shutil import copy2

from calculix import execute_cgx, execute_fea

PLOT_FLAG = True


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

    # check input files have been uploaded
    if not (inputs_folder / setup_data["param_input_files.cgx_file"]).is_file():
        raise FileNotFoundError(
            f"{setup_data['param_input_files.cgx_file']} param file connection needed from parametric-model component."
        )
    if not (inputs_folder / params["analysis_file"]).is_file():
        raise FileNotFoundError(
            f"{params['analysis_file']} needs to be uploaded by the user."
        )

    print("Starting user function evaluation.")

    # Generate the ccx input mesh with cgx
    infile = copy2(
        inputs_folder / setup_data["param_input_files.cgx_file"],
        run_folder / setup_data["param_input_files.cgx_file"],
    )
    resp = execute_cgx(infile.name, run_folder=run_folder)
    with open(run_folder / "cgx.log", "w") as f:
        f.write(resp)

    # check output has been saved
    mesh_file_path = run_folder / params["mesh_file"]
    if not mesh_file_path.is_file():
        FileNotFoundError(f"{str(mesh_file_path)} is not a file.")
    print("Created CCX analysis mesh file with CGX.")

    # define composite material properties
    if "composite_layup" in params:
        get_composite_properties_input(params, run_folder)
        print("Created CCX composite properties file.")

    # run the FEM model analysis
    infile = copy2(
        inputs_folder / params["analysis_file"], run_folder / params["analysis_file"]
    )
    resp = execute_fea(infile.stem, run_folder=run_folder)
    with open(run_folder / "ccx.log", "w") as f:
        f.write(resp)

    # check output has been saved
    outfile = run_folder / (infile.stem + ".dat")
    if not outfile.is_file():
        FileNotFoundError(f"{str(outfile)} is not a file.")
    print("Executed CCX FEM analysis.")

    # set outputs
    # outputs = {"output_files": [outfile.name]}
    message = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}: Executed Calculix finite element analysis."
    print(message)

    return {
        "message": message,
        "output_files.analysis_output_file": outfile.name,
        "output_files.mesh_file": "all.msh",
        "output_files.nodeset_file": "LAST.nam",
    }


def get_composite_properties_input(inputs, run_folder):
    """write an FEA input file with the composite properties."""

    # check and update the element type in the mesh input file
    str_find = "*ELEMENT, TYPE=S8,"
    str_replace = "*ELEMENT, TYPE=S8R,"
    _file_find_replace(
        file=(run_folder / inputs["mesh_file"]),
        find=str_find,
        replace_with=str_replace,
    )

    if "filled_sections_flags" in inputs and not isinstance(
        inputs["filled_sections_flags"], list
    ):
        inputs["filled_sections_flags"] = [inputs["filled_sections_flags"]]

    shell_set_name = inputs["shell_set_name"]
    if "filled_sections_flags" in inputs and any(inputs["filled_sections_flags"]):

        if not (
            isinstance(inputs["airfoil_cut_chord_percentages"], list)
            and len(inputs["airfoil_cut_chord_percentages"]) == 2
        ):
            raise ValueError(
                "if 'filled_sections_flags' is switched on, 'airfoil_cut_chord_percentages'"
                "should be a list of length 2."
            )

        # create separate element sets for shells and solids
        str_find = "*ELEMENT, TYPE=S8R, ELSET=Eall"
        str_replace = "*ELEMENT, TYPE=S8R, ELSET=SURF"
        _file_find_replace(
            file=(run_folder / inputs["mesh_file"]),
            find=str_find,
            replace_with=str_replace,
        )
        str_find = "*ELEMENT, TYPE=C3D20, ELSET=Eall"
        str_replace = "*ELEMENT, TYPE=C3D20, ELSET=CORE"
        _file_find_replace(
            file=(run_folder / inputs["mesh_file"]),
            find=str_find,
            replace_with=str_replace,
        )

    # get input file cards for this solver
    ccx_commands = _get_ccx_composite_shell_props(
        plies=inputs["composite_plies"],
        orientations=inputs["orientations"],
        layup=inputs["composite_layup"],
        shell_set_name=shell_set_name,
    )

    # write string of commands to file
    with open(run_folder / inputs["composite_props_file"], "w", encoding="utf-8") as f:
        f.write("".join(ccx_commands))


########### Private functions that do not get called directly


def _file_find_replace(file, find: str, replace_with: str):
    with open(file, "r", encoding="utf-8") as f:
        contents = f.readlines()

    for index, line in enumerate(contents):
        if find in line:
            contents[index] = line.replace(find, replace_with)
            print(f"Find & Replace edited file '{file}' at line {index:d}.")
            break

    with open(file, "w", encoding="utf-8") as f:
        f.write("".join(contents))


def _get_ccx_composite_shell_props(
    plies=None, orientations=None, layup=None, shell_set_name=None
):

    commands = []
    if not shell_set_name:
        shell_set_name = {"ribs": "ERIBS", "aero": "EAERO"}

    # orientation cards
    for ori in orientations:
        commands.append(f"*ORIENTATION,NAME={ori['id']}\n")
        commands.append(", ".join(str(x) for x in [*ori["1"], *ori["2"]]) + "\n")

    commands.append("** =============== \n")
    # shell property
    for (key, section_name) in shell_set_name.items():
        commands.append(f"*SHELL SECTION,ELSET={section_name},COMPOSITE\n")
        for ply in layup[key]:
            props = [p for p in plies if p["id"] == ply][0]
            commands.append(
                f"{props['thickness']:6f},,{props['material']},{props['orientation']}\n"
            )

    return commands
