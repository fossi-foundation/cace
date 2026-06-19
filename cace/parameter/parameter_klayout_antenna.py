# Copyright 2026 CACE Contributors
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
import glob
from typing import (
    Optional,
    List,
    Any,
)

from ..config import Variable, Result
from ..common.types import Path
from ..common.common import run_subprocess, get_pdk_root, get_layout_path
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


@register_parameter("klayout_antenna_check")
class ParameterKLayoutAntenna(Parameter):
    """
    Run antenna check using KLayout to find antenna violations in the layout.
    """

    id = "KLayout.AntennaCheck"
    name = "Antenna check (KLayout)"

    config_vars = [
        Variable(
            "jobs",
            int,
            "Number of jobs (threads) to use in parallel.",
            default=1,
        ),
        Variable(
            "args",
            Optional[List[str]],
            "Additional arguments.",
        ),
        Variable(
            "drc_script_path",
            Optional[Path],
            "Optional path to a custom KLayout antenna script..",
        ),
    ]

    config_results = [
        Result(
            "antenna_violations",
            Any,
            "The number of antenna violations.",
        ),
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
            info("Netlist source is schematic capture. Not running antenna checks.")
            self.result_type = ResultType.SKIPPED
            return False

        return True

    def implementation(self):

        self.cancel_point()

        jobs = self.config["jobs"]

        if jobs == "max":
            # Set the number of jobs to the number of cores
            jobs = os.cpu_count()
        else:
            # Make sure that jobs don't exceed max jobs
            jobs = min(jobs, os.cpu_count())

        # Acquire job(s) from the global jobs semaphore
        self.jobs_sem.acquire(jobs)

        projname = self.datasheet["name"]
        paths = self.datasheet["paths"]

        info("Running KLayout to get antenna report.")

        # Get the path to the layout, only GDS
        layout_filepath, is_magic = get_layout_path(
            projname, self.paths, check_magic=False
        )

        # Check if layout exists
        if not os.path.isfile(layout_filepath):
            err("No layout found!")
            self.result_type = ResultType.ERROR
            self.jobs_sem.release(jobs)
            return

        drc_script_path = self.config["drc_script_path"]

        if drc_script_path == None:
            if self.datasheet["PDK"].startswith("ihp-sg13"):
                drc_script_path = os.path.join(
                    get_pdk_root(),
                    self.datasheet["PDK"],
                    "libs.tech",
                    "klayout",
                    "tech",
                    "drc",
                    "rule_decks",
                    "antenna.drc",
                )

        if not os.path.exists(drc_script_path):
            err(f"DRC script {drc_script_path} does not exist!")
            self.result_type = ResultType.ERROR
            self.jobs_sem.release(jobs)
            return

        report_file_path = os.path.join(self.param_dir, "report.xml")

        arguments = []

        # PDK specific arguments
        if self.datasheet["PDK"].startswith("ihp-sg13"):
            arguments = [
                "-b",
                "-r",
                drc_script_path,
                "-rd",
                f"input={os.path.abspath(layout_filepath)}",
                "-rd",
                f"topcell={projname}",
                "-rd",
                f"report={report_file_path}",
                "-rd",
                f"threads={jobs}",
            ]

        if self.config["args"]:
            arguments.extend(self.config["args"])

        returncode = self.run_subprocess(
            "klayout",
            arguments,
            cwd=self.param_dir,
        )

        # Free job(s) from the global jobs semaphore
        self.jobs_sem.release(jobs)

        # Advance progress bar
        if self.step_cb:
            self.step_cb(self.param)

        if not os.path.isfile(report_file_path):
            err("No output file generated by KLayout!")
            err(f"Expected file: {report_file_path}")
            self.result_type = ResultType.ERROR
            return

        info(
            f"KLayout antenna report at '[repr.filename][link=file://{os.path.abspath(report_file_path)}]{os.path.relpath(report_file_path)}[/link][/repr.filename]'…"
        )

        # Get the result
        try:
            with open(report_file_path) as klayout_xml_report:
                size = os.fstat(klayout_xml_report.fileno()).st_size
                if size == 0:
                    err(f"File {report_file_path} is of size 0.")
                    self.result_type = ResultType.ERROR
                    return
                antenna_content = klayout_xml_report.read()
                antenna_vio_count = antenna_content.count("<item>")

                self.result_type = ResultType.SUCCESS
                self.get_result("antenna_violations").values = [antenna_vio_count]
                return

        # Catch reports not found
        except FileNotFoundError as e:
            err(f"Failed to generate {report_file_path}: {e}")
            self.result_type = ResultType.ERROR
            return
        except (IOError, OSError) as e:
            err(f"Failed to generate {report_file_path}: {e}")
            self.result_type = ResultType.ERROR
            return
