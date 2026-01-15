# Copyright 2023 Efabless Corporation
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

import inspect
import textwrap
from enum import Enum
from dataclasses import (
    dataclass,
    is_dataclass,
)
import types
from typing import (
    Any,
    Optional,
    Iterable,
    Type,
    Union,
    Literal,
    get_origin,
    get_args,
)

def is_optional(t: Type[Any]) -> bool:
    type_args = get_args(t)
    origin = get_origin(t)
    return (origin is Union or origin is types.UnionType) and type(None) in type_args

def some_of(t: Type[Any]) -> Type[Any]:
    if not is_optional(t):
        return t

    # t must be a Union with None if we're here

    type_args = get_args(t)
    origin = get_origin(t)

    args_without_none = [arg for arg in type_args if arg is not type(None)]
    if len(args_without_none) == 1:
        return args_without_none[0]

    if origin is types.UnionType:
        # Use the | operator to create a UnionType
        result = args_without_none[0]
        for arg in args_without_none[1:]:
            result = result | arg
        return result

    # Otherwise, return a typing.Union
    new_union = Union[tuple(args_without_none)]  # type: ignore
    return new_union  # type: ignore

def repr_type(t: Type[Any], for_document: bool = False) -> str:  # pragma: no cover
    optional = is_optional(t)
    some = some_of(t)

    if hasattr(some, "__name__"):  # Python 3.10+
        type_string = some.__name__
    else:
        type_string = str(some)

    if is_dataclass(t):
        type_string = (
            f"{{class}}`{some.__qualname__} <{some.__module__}.{some.__qualname__}>`"
        )

    separator = "｜<br />" if for_document else "｜"

    if inspect.isclass(some) and issubclass(some, Enum):
        type_string = separator.join([str(e.name) for e in some])
        type_string = f"`{type_string}`"
    else:
        origin, args = get_origin(some), get_args(some)
        if origin is not None:
            if origin == Union:
                arg_strings = [repr_type(arg) for arg in args]
                type_string = separator.join(arg_strings)
                type_string = f"({type_string})"
            elif origin == Literal:
                return separator.join([repr(arg) for arg in args])
            else:
                arg_strings = [repr_type(arg) for arg in args]
                type_string = f"{type_string}[{', '.join(arg_strings)}]"

    return type_string + ("?" if optional else "")

@dataclass
class Result:
    """
    A result of a tool.
    """

    name: str
    type: Any
    description: str
    default: Any = None
    
    units: Optional[str] = None

    def type_repr_md(self, for_document: bool = False) -> str:  # pragma: no cover
        """
        :param for_document: Adds HTML line breaks between sum type separators
            for easier wrapping by web browsers/PDF renderers/what have you
        :returns: A pretty Markdown string representation of the Variable's type.
        """
        return repr_type(self.type, for_document=for_document)

    def desc_repr_md(self) -> str:  # pragma: no cover
        """
        :returns: The description, but with newlines escaped for Markdown.
        """
        return self.description.replace("\n", "<br />")

    @staticmethod
    def _render_table_md(
        vars: Iterable["Variable"],
        *,
        myst_anchor_owner_id: Optional[str] = None,
    ) -> str:  # pragma; no cover
        """
        Renders a markdown table for any iterable of configuration variables.

        :param vars: Any iterable object returning configuration variables
        :param myst_anchor_owner_id:
            If set, the table is rendered for MyST using a mix of HTML and
            Markdown, with anchors and a detail tag containing deprecated names.

            For universal flow variables, set the anchor id to "".
        :returns: A markdown string representing the table
        """
        include_units = any(c.units is not None for c in vars)
        if myst_anchor_owner_id is None:
            # Markdown mode
            result = textwrap.dedent(
                f"""
                | Variable Name | Type | Description | {'Units |' * include_units}
                | - | - | - | {'- |' * include_units}
                """
            )
            for var in vars:
                units = var.units or ""
                result += f"| `{var.name}` | {var.type_repr_md(for_document=True)} | {var.desc_repr_md()} |"
                if include_units:
                    result += f" {units} |"
                result += "\n"
            result += "\n"
        else:
            if myst_anchor_owner_id == "":
                # for _get_docs_identifier, where None is the behavior we want
                # for a literal ""
                myst_anchor_owner_id = None
            result = textwrap.dedent(
                f"""
                <div class="table-wrapper colwidths-auto docutils container">
                <table class="docutils align-default">
                <thead><tr>
                <th class="head">Variable Name</th>
                <th class="head">Type</th>
                <th class="head">Description</th>
                {'<th class="head">Units</th>' * include_units}
                </tr></thead>
                <tbody>
                """
            )
            for var in vars:
                units = var.units or ""

                result += textwrap.dedent(
                    f"""
                    <tr>
                    <td>

                    `{var.name}`
                    """
                )
                result += textwrap.dedent(
                    f"""
                    </td>
                    <td>

                    {var.type_repr_md(for_document=True)}

                    </td>
                    <td>

                    {var.desc_repr_md()}

                    </td>
                    """
                )
                result += include_units * textwrap.dedent(
                    f"""
                    <td>

                    {units}

                    </td>
                    """
                )
                result += "\n</tr>"
            result += "</tbody></table></div>\n"
        return result
