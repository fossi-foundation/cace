#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2024 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
import traceback

import jinja2
from sphinx.config import Config
from sphinx.application import Sphinx

import cace
import cace.parameter

from cace.parameter import registered_parameters

def setup(app: Sphinx):
    app.connect("config-inited", generate_module_docs)
    return {"version": "1.0"}


def generate_module_docs(app: Sphinx, conf: Config):
    try:
        conf_py_path: str = conf._raw_config["__file__"]
        doc_root_dir: str = os.path.dirname(conf_py_path)

        template_relpath: str = conf.templates_path[0]
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.abspath(os.path.join(current_file_path, "..", template_relpath, "generate_docs"))
        
        lookup = jinja2.FileSystemLoader(searchpath=template_path)

        # Mako-like environment
        env = jinja2.Environment(
            "<%",
            "%>",
            "${",
            "}",
            "<%doc>",
            "</%doc>",
            "%",
            "##",
            loader=lookup,
        )
        
        class Parameter:
            def __init__(self, name="None"):
                self.name = name
            
            def get_help_md(self, use_dropdown=False, myst_anchors=False):
                return self.name

        print(registered_parameters)

        categories_sorted = [
            ("Category 1", [
                    ("KLayout", Parameter("KLayout")),
                    ("magic", Parameter()),
                ]
            ),
            ("Category 2", [
                    ("netgen", Parameter()),
                    ("ngspice", Parameter()),
                ]
            ),
        ]

        # --

        template = env.get_template("parameters.md")
        with open(
            os.path.join(doc_root_dir, "reference", "parameters.md"), "w"
        ) as f:
            f.write(
                template.render(
                    #slugify=slugify,
                    categories_sorted=categories_sorted,
                )
            )

    except Exception:
        print(traceback.format_exc())
        exit(-1)
