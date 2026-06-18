# Copyright 2024 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys
import math
import json
import threading
import subprocess
from typing import (
    Optional,
    List,
    Any,
)

from ..config import Variable, Result
from ..common.common import run_subprocess, get_magic_rcfile, get_layout_path
from ..common.ring_buffer import RingBuffer
from .parameter import Parameter, ResultType, NamedResult
from .registry import register_parameter
from ..logging import (
    dbg,
    verbose,
    info,
    subproc,
    rule,
    success,
    warn,
    err,
)


@register_parameter("magic_area")
class ParameterMagicArea(Parameter):
    """
    Take measurements of the layout geometry using magic.
    """

    id = "Magic.Geometry"
    name = "Get area, width and height (Magic)"

    config_vars = [
        Variable(
            "args",
            Optional[List[str]],
            "Additional arguments.",
        ),
    ]

    config_results = [
        Result("area", Any, "The area of the layout.", units="μm²"),
        Result("width", Any, "The width of the layout.", units="μm"),
        Result("height", Any, "The height of the layout.", units="μm"),
    ]

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

    def is_runnable(self):
        netlist_source = self.runtime_options["netlist_source"]

        if netlist_source == "schematic":
            info("Netlist source is schematic capture. Not running area measurements.")
            self.result_type = ResultType.SKIPPED
            return False

        return True

    def implementation(self):

        self.cancel_point()

        # Acquire a job from the global jobs semaphore
        with self.jobs_sem:

            info(f"Running magic to get area measurements.")

            projname = self.datasheet["name"]
            paths = self.datasheet["paths"]

            rcfile = get_magic_rcfile()

            # Get the path to the layout, prefer magic
            layout_filepath, is_magic = get_layout_path(
                projname, self.paths, check_magic=True
            )

            # Check if layout exists
            if not os.path.isfile(layout_filepath):
                err("No layout found!")
                self.result_type = ResultType.ERROR
                return

            # Run magic to get the bounds of the design geometry
            # Get triplet of area, width, and height

            magic_input = ""

            if is_magic:
                magic_input += f"path search +{os.path.abspath(os.path.dirname(layout_filepath))}\n"
                magic_input += f"load {os.path.basename(layout_filepath)}\n"
            else:
                magic_input += f"gds read {os.path.abspath(layout_filepath)}\n"
                magic_input += "set toplist [cellname list top]\n"
                magic_input += "set numtop [llength $toplist]\n"
                magic_input += "if {$numtop > 1} {\n"
                magic_input += "   foreach topcell $toplist {\n"
                magic_input += '      if {$topcell != "(UNNAMED)"} {\n'
                magic_input += "         load $topcell\n"
                magic_input += "         break\n"
                magic_input += "      }\n"
                magic_input += "   }\n"
                magic_input += "}\n"

            magic_input += "select top cell\n"
            magic_input += "box\n"
            magic_input += "quit -noprompt\n"

            arguments = ["-dnull", "-noconsole", "-rcfile", rcfile]

            if self.config["args"]:
                arguments.extend(self.config["args"])

            returncode = self.run_subprocess(
                "magic",
                arguments,
                input=magic_input,
                cwd=self.param_dir,
            )

            if returncode != 0:
                err("Magic exited with non-zero return code!")

            magrex = re.compile(
                "microns:[ \t]+([0-9.]+)[ \t]*x[ \t]*([0-9.]+)[ \t]+.*[ \t]+([0-9.]+)[ \t]*$"
            )

            with open(
                f'{os.path.join(self.param_dir, "magic")}_stdout.out', "r"
            ) as stdout_file:

                for line in stdout_file.readlines():
                    lmatch = magrex.match(line)
                    if lmatch:
                        widthval = float(lmatch.group(1)) / 1000_000
                        heightval = float(lmatch.group(2)) / 1000_000
                        areaval = float(lmatch.group(3)) / 1000_000 / 1000_000

        self.result_type = ResultType.SUCCESS

        self.get_result("area").values = [areaval]
        self.get_result("width").values = [widthval]
        self.get_result("height").values = [heightval]

        # Increment progress bar
        if self.step_cb:
            self.step_cb(self.param)
