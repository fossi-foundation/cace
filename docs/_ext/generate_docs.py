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

from cace.common import slugify
from cace.parameter.registry import get_tools

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
        
        
        # Pre-processing
        by_category = {}
        for param in get_tools().values():
            category, _ = param.id.split(".")
            if by_category.get(category) is None:
                by_category[category] = []
            by_category[category].append(param)

        print(by_category)

        misc = ("Misc", by_category.get("Misc",[]))
        if "Misc" in by_category:
            del by_category["Misc"]

        print(by_category.items())

        ## Sort Categories
        categories_sorted = list(sorted(by_category.items(), key=lambda c: c[0])) + [
            misc
        ]

        print(categories_sorted)

        ## Sort Steps
        for i in range(0, len(categories_sorted)):
            category, step_list = categories_sorted[i]
            steps_sorted = list(sorted(step_list, key=lambda s: s.id))
            categories_sorted[i] = (category, steps_sorted)

        print(categories_sorted)


        # --

        template = env.get_template("tools.md")
        with open(
            os.path.join(doc_root_dir, "reference", "tools.md"), "w"
        ) as f:
            f.write(
                template.render(
                    slugify=slugify,
                    categories_sorted=categories_sorted,
                )
            )

    except Exception:
        print(traceback.format_exc())
        exit(-1)
