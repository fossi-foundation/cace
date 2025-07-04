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

from ..common.common import run_subprocess, get_pdk_root, get_layout_path
from .parameter import Parameter, ResultType, Argument, Result
from .parameter_manager import register_parameter
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


@register_parameter('klayout_drc')
class ParameterKLayoutDRC(Parameter):
    """
    Run KLayout drc
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.add_result(Result('drc_errors'))

        self.add_argument(Argument('jobs', 1, False))
        self.add_argument(Argument('args', [], False))
        self.add_argument(Argument('drc_script_path', None, False))

    def is_runnable(self):
        netlist_source = self.runtime_options['netlist_source']

        if netlist_source == 'schematic':
            info('Netlist source is schematic capture. Not running DRC.')
            self.result_type = ResultType.SKIPPED
            return False

        return True

    def implementation(self):

        self.cancel_point()

        jobs = self.get_argument('jobs')

        if jobs == 'max':
            # Set the number of jobs to the number of cores
            jobs = os.cpu_count()
        else:
            # Make sure that jobs don't exceed max jobs
            jobs = min(jobs, os.cpu_count())

        # Acquire job(s) from the global jobs semaphore
        self.jobs_sem.acquire(jobs)

        projname = self.datasheet['name']
        paths = self.datasheet['paths']

        info('Running KLayout to get DRC report.')

        # Get the path to the layout, only GDS
        (layout_filepath, is_magic) = get_layout_path(
            projname, self.paths, check_magic=False
        )

        # Check if layout exists
        if not os.path.isfile(layout_filepath):
            err('No layout found!')
            self.result_type = ResultType.ERROR
            self.jobs_sem.release(jobs)
            return

        drc_script_path = self.get_argument('drc_script_path')

        if drc_script_path == None:
            if self.datasheet['PDK'].startswith('sky130'):
                drc_script_path = os.path.join(
                    get_pdk_root(),
                    self.datasheet['PDK'],
                    'libs.tech',
                    'klayout',
                    'drc',
                    f'{self.datasheet["PDK"]}_mr.drc',
                )
            if self.datasheet['PDK'].startswith('ihp-sg13g2'):
                drc_script_path = os.path.join(
                    get_pdk_root(),
                    self.datasheet['PDK'],
                    'libs.tech',
                    'klayout',
                    'tech',
                    'drc',
                    'sg13g2_maximal.lydrc',
                )

        if not os.path.exists(drc_script_path):
            err(f'DRC script {drc_script_path} does not exist!')
            self.result_type = ResultType.ERROR
            self.jobs_sem.release(jobs)
            return

        report_file_path = os.path.join(self.param_dir, 'report.xml')

        arguments = []

        # PDK specific arguments
        if self.datasheet['PDK'].startswith('sky130'):
            arguments = [
                '-b',
                '-r',
                drc_script_path,
                '-rd',
                f'input={os.path.abspath(layout_filepath)}',
                '-rd',
                f'topcell={projname}',
                '-rd',
                f'report={report_file_path}',
                '-rd',
                f'thr={os.cpu_count()}',
            ]
        if self.datasheet['PDK'].startswith('ihp-sg13g2'):
            arguments = [
                '-b',
                '-r',
                drc_script_path,
                '-rd',
                f'in_gds={os.path.abspath(layout_filepath)}',
                '-rd',
                f'cell={projname}',
                '-rd',
                f'report_file={report_file_path}',
                '-rd',
                f'threads={os.cpu_count()}',
            ]

        returncode = self.run_subprocess(
            'klayout',
            arguments + self.get_argument('args'),
            cwd=self.param_dir,
        )

        # Free job(s) from the global jobs semaphore
        self.jobs_sem.release(jobs)

        # Advance progress bar
        if self.step_cb:
            self.step_cb(self.param)

        if not os.path.isfile(report_file_path):
            err('No output file generated by KLayout!')
            err(f'Expected file: {report_file_path}')
            self.result_type = ResultType.ERROR
            return

        info(
            f"KLayout DRC report at '[repr.filename][link=file://{os.path.abspath(report_file_path)}]{os.path.relpath(report_file_path)}[/link][/repr.filename]'…"
        )

        # Get the result
        try:
            with open(report_file_path) as klayout_xml_report:
                size = os.fstat(klayout_xml_report.fileno()).st_size
                if size == 0:
                    err(f'File {report_file_path} is of size 0.')
                    self.result_type = ResultType.ERROR
                    return
                drc_content = klayout_xml_report.read()
                drc_count = drc_content.count('<item>')

                self.result_type = ResultType.SUCCESS
                self.get_result('drc_errors').values = [drc_count]
                return

        # Catch reports not found
        except FileNotFoundError as e:
            err(f'Failed to generate {report_file_path}: {e}')
            self.result_type = ResultType.ERROR
            return
        except (IOError, OSError) as e:
            err(f'Failed to generate {report_file_path}: {e}')
            self.result_type = ResultType.ERROR
            return
