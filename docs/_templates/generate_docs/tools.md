# Parameters and their Configuration Variables

These are the parameters available in CACE. Use their IDs to specify the parameters in the datasheet.

Configuration variables are used to configure the behavior of the parameters.

%for category, parameters in categories_sorted:

${"##"} ${category}

%for parameter in parameters:
${parameter.get_help_md(use_dropdown=True, myst_anchors=True)}
<hr />

%endfor

%endfor

## Missing a Tool?

If you're missing a tool or functionality, please open an issue [here](https://github.com/efabless/cace/issues).
