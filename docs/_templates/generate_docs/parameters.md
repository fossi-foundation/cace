# Parameters and their Configuration Variables

Bla bla bla

%for category, parameters in categories_sorted:
${"##"} ${category}
%for key, parameter in parameters:
${parameter.get_help_md(use_dropdown=True, myst_anchors=True)}
<hr />

%endfor
<hr />

%endfor
