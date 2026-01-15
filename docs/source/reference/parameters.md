# Parameters and their Configuration Variables

These are the parameters available in CACE. Use their IDs to specify the parameters in the datasheet.

Configuration variables are used to configure the behavior of the parameters.

## KLayout


(step-klayout-drc)=
### Design Rule Check (KLayout)
ID: `KLayout.DRC`

Run DRC using KLayout.

(klayout.drc-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`jobs`

</td>
<td>

(int｜<br />'max')

</td>
<td>

Number of jobs to run in parallel.

</td>
<td>

`1`

</td>

</tr>
<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`drc_script_path`

</td>
<td>

Path?

</td>
<td>

Custom KLayout DRC script.

</td>
<td>

`None`

</td>

</tr></tbody></table></div>

(klayout.drc-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>

</tr></thead>
<tbody>

<tr>
<td>

`drc_errors`

</td>
<td>

Any

</td>
<td>

The number of DRC errors.

</td>

</tr></tbody></table></div>

<hr />


(step-klayout-lvs)=
### Layout Versus Schematic (KLayout)
ID: `KLayout.LVS`

Run LVS using KLayout.

(klayout.lvs-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`script`

</td>
<td>

Path?

</td>
<td>

Custom LVS script.

</td>
<td>

`None`

</td>

</tr></tbody></table></div>

(klayout.lvs-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>

</tr></thead>
<tbody>

<tr>
<td>

`lvs_errors`

</td>
<td>

Any

</td>
<td>

The number of LVS errors.

</td>

</tr></tbody></table></div>

<hr />

## Magic


(step-magic-antennacheck)=
### Antenna check (Magic)
ID: `Magic.AntennaCheck`

Run antenna check using magic to
find antenna violations in the layout.

(magic.antennacheck-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`gds_flatten`

</td>
<td>

bool

</td>
<td>

Flatten the GDS before running the check.

</td>
<td>

`False`

</td>

</tr></tbody></table></div>

(magic.antennacheck-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>

</tr></thead>
<tbody>

<tr>
<td>

`antenna_violations`

</td>
<td>

Any

</td>
<td>

The number of antenna violations.

</td>

</tr></tbody></table></div>

<hr />


(step-magic-drc)=
### Design Rule Check (Magic)
ID: `Magic.DRC`

Run DRC using magic.

(magic.drc-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`gds_flatten`

</td>
<td>

bool

</td>
<td>

Flatten the GDS before running the check.

</td>
<td>

`False`

</td>

</tr></tbody></table></div>

(magic.drc-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>

</tr></thead>
<tbody>

<tr>
<td>

`drc_errors`

</td>
<td>

Any

</td>
<td>

The number of DRC errors.

</td>

</tr></tbody></table></div>

<hr />


(step-magic-geometry)=
### Get area, width and height (Magic)
ID: `Magic.Geometry`

Determine bounds of the design geometry using magic.

The returns the width and height values in microns.

(magic.geometry-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr></tbody></table></div>

(magic.geometry-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Units</th>
</tr></thead>
<tbody>

<tr>
<td>

`area`

</td>
<td>

Any

</td>
<td>

The area of the layout.

</td>

<td>

μm²

</td>

</tr>
<tr>
<td>

`width`

</td>
<td>

Any

</td>
<td>

The width of the layout.

</td>

<td>

μm

</td>

</tr>
<tr>
<td>

`height`

</td>
<td>

Any

</td>
<td>

The height of the layout.

</td>

<td>

μm

</td>

</tr></tbody></table></div>

<hr />

## Netgen


(step-netgen-lvs)=
### Layout Versus Schematic (Netgen)
ID: `Netgen.LVS`

Run LVS using netgen.

```{note}
The `netgen_lvs` tool always compares the `schematic` netlist with the `layout` extracted netlist, independent of the selected netlist source.
```

(netgen.lvs-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`args`

</td>
<td>

List[str]?

</td>
<td>

Additional arguments.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`script`

</td>
<td>

Path?

</td>
<td>

Custom netgen LVS script.

</td>
<td>

`None`

</td>

</tr></tbody></table></div>

(netgen.lvs-configuration-results)=
#### Results

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>

</tr></thead>
<tbody>

<tr>
<td>

`lvs_errors`

</td>
<td>

Any

</td>
<td>

The number of LVS errors.

</td>

</tr></tbody></table></div>

<hr />

## Ngspice


(step-ngspice-simulation)=
### Simulation (Ngspice)
ID: `Ngspice.Simulation`

Run simulations using ngspice.

(ngspice.simulation-configuration-variables)=
#### Configuration Variables

<div class="table-wrapper colwidths-auto docutils container">
<table class="docutils align-default">
<thead><tr>
<th class="head">Variable Name</th>
<th class="head">Type</th>
<th class="head">Description</th>
<th class="head">Default</th>

</tr></thead>
<tbody>

<tr>
<td>

`jobs`

</td>
<td>

(int｜<br />'max')

</td>
<td>

Number of jobs to run in parallel.

</td>
<td>

`1`

</td>

</tr>
<tr>
<td>

`template`

</td>
<td>

Path

</td>
<td>

Path to the template testbench.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`collate`

</td>
<td>

str?

</td>
<td>

Merge runs with the same conditions but different iterations. This is used for plotting

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`format`

</td>
<td>

'ascii'

</td>
<td>

Output format of the testbench simulation result file.

</td>
<td>

`ascii`

</td>

</tr>
<tr>
<td>

`suffix`

</td>
<td>

str

</td>
<td>

Suffix of the testbench simulation result file.

</td>
<td>

`.data`

</td>

</tr>
<tr>
<td>

`variables`

</td>
<td>

List[str?]

</td>
<td>

The variables of the template testbench, configured in the conditions section.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`script`

</td>
<td>

Path?

</td>
<td>

Postprocessing using user-defined Python script.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`script_variables`

</td>
<td>

List[str?]?

</td>
<td>

Output variables of the user-defined Python script.

</td>
<td>

`None`

</td>

</tr>
<tr>
<td>

`spiceinit_path`

</td>
<td>

Path?

</td>
<td>

Specify a spiceinit other than the PDK spiceinit.

</td>
<td>

`None`

</td>

</tr></tbody></table></div>

<hr />

## Misc

