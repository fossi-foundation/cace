# A simple 5-transistor OTA ![](../../workflows/cace/badge.svg)

This example showcases how to setup a project for [CACE](https://github.com/fossi-foundation/cace).

- [Documentation](docs/sg13g2_cace_ip__ota5t.md)
- [Characterization](docs/sg13g2_cace_ip__ota5t_rcx.md)

# Repository Structure

Besides the normal directories such as `xschem/` for the schematic and testbench and `gds/` for the layout, there is also the `cace/` subdirectory.
Here you will find the CACE datasheet for this project named `sg13g2_cace_ip__ota5t.yaml`, which contains the specification for the design and represents the configuration for CACE.

In the `templates/` subdirectory you will find some xschem testbench. These are not a normal testbenches, but instead acts as templates for CACE.
They contain placeholders for various conditions such as `CACE{temperature}` or `CACE{corner}`, which will get substituted by CACE  to generate the final simulation testbenches.

The subdirectory `scripts/` contains all user-defined scripts, in this case a custom script `run_project_lvs.tcl` to run LVS.

# Run CACE

After you have installed CACE and all dependencies, invoking the characterization of this project is as easy as running:

```console
cace
```

This will use the "best" netlist available. Since a layout is provided, the netlist source will be "rcx" (R-C-extracted). To perform characterization on a different netlist, pass the `--source` argument to cace. For help on arguments, run `cace --help`.

After characterization is completed, you will find the simulation files, log files and reports under `run/TIMESTAMP/`, where TIMESTAMP is the time and date when cace was started.

# Continuous Integration

This project also demonstrates how CACE can be used for continuous integration. Under `.github/workflows/` you will find the `ci.yml` GitHub action. It makes use of the composite action [cace-action](https://github.com/mole99/cace-action).

First, the environment is set up and CACE is started. Then the `run/` directory is uploaded so that it can be viewed later. Finally, the summary is added to the step overview.

Take a look at the latest runs under [actions](https://github.com/mole99/sg13g2_cace_ip__ota5t/actions). If you are logged in to GitHub, you can also click on a run and view the summary.


