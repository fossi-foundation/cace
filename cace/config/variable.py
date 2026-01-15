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
from decimal import Decimal, InvalidOperation
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

from ..common.types import Path, is_string
from ..common.misc import zip_first

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
class Variable:
    """
    A variable for configuring tools.
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
                | Variable Name | Type | Description | Default | {'Units |' * include_units}
                | - | - | - | - | {'- |' * include_units}
                """
            )
            for var in vars:
                units = var.units or ""
                result += f"| `{var.name}` | {var.type_repr_md(for_document=True)} | {var.desc_repr_md()} | `{var.default}` |"
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
                <th class="head">Default</th>
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
                    <td>

                    `{var.default}`

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

    def __process(
        self,
        key_path: str,
        value: Any,
        validating_type: Type[Any],
        default: Any = None,
        explicitly_specified: bool = True,
        permissive_typing: bool = False,
        depth: int = 0,
    ):
        if value is None:
            if explicitly_specified:
                # User explicitly specified "null" for this value: only error if
                # value is not optional
                if not is_optional(validating_type):
                    raise ValueError(
                        f"Non-optional variable '{key_path}' explicitly assigned a null value."
                    )
                else:
                    return None
            else:
                # User did not specify a value for this variable: couple outcomes
                if default is not None:
                    return self.__process(
                        key_path=key_path,
                        value=default,
                        validating_type=validating_type,
                        permissive_typing=permissive_typing,
                        depth=depth + 1,
                    )
                elif not is_optional(validating_type):
                    if depth == 0:
                        raise MissingRequiredVariable(self, self.pdk)
                    else:
                        raise ValueError(f"'{key_path}' must be non-null.")
                else:
                    return None

        if is_optional(validating_type):
            validating_type = some_of(validating_type)

        type_origin = get_origin(validating_type)
        type_args = get_args(validating_type)

        if type_origin in [list, tuple]:
            return_value = list()
            raw = value
            if isinstance(raw, list) or isinstance(raw, tuple):
                # HACK: Allow multiple globs within Path variables
                if type_origin is list and type_args == (Path,):
                    if any(isinstance(item, List) for item in raw):
                        Variable.__flatten_list(value)
                pass  # do nothing, can be used as is
            elif is_string(raw):
                if not permissive_typing:
                    raise ValueError(
                        f"Refusing to automatically convert string at '{key_path}' to list"
                    )
                if "," in raw:
                    raw = raw.split(",")
                elif ";" in raw:
                    raw = raw.split(";")
                else:
                    raw = raw.split()
                if len(raw) and raw[-1] == "":
                    raw.pop()  # Trailing commas
            else:
                raise ValueError(
                    f"List provided for variable '{key_path}' is invalid: {value}"
                )

            if type_origin is tuple:
                if len(raw) != len(type_args):
                    raise ValueError(
                        f"Value provided for variable '{key_path}' of type {validating_type} is invalid: ({len(raw)}/{len(type_args)}) tuple entries provided"
                    )

            for i, (item, value_type) in enumerate(
                zip_first(raw, type_args, fillvalue=type_args[0])
            ):
                return_value.append(
                    self.__process(
                        key_path=f"{key_path}[{i}]",
                        value=item,
                        validating_type=value_type,
                        permissive_typing=permissive_typing,
                        depth=depth + 1,
                    )
                )

            if type_origin is tuple:
                return tuple(return_value)

            return return_value
        elif type_origin is dict:
            raw = value
            key_type, value_type = type_args
            if isinstance(raw, dict):
                pass
            elif isinstance(raw, list) or is_string(raw):
                if not permissive_typing:
                    raise ValueError(
                        f"Refusing to automatically convert string at '{key_path}' to dict"
                    )
                components = raw
                if is_string(raw):
                    components = shlex.split(raw)
                assert isinstance(components, list)
                # Assuming Tcl format:
                if len(components) % 2 != 0:
                    raise ValueError(
                        f"Tcl-style flat dictionary provided for variable '{key_path}' is invalid: uneven number of components ({len(components)})"
                    )
                raw = {}
                for i in range(0, len(components) // 2):
                    key = components[2 * i]
                    val = components[2 * i + 1]
                    raw[key] = val
            else:
                raise ValueError(
                    f"Value provided for variable '{key_path}' of type {validating_type} is invalid: '{value}'"
                )

            processed = {}
            for key, val in raw.items():
                key_validated = self.__process(
                    key_path=key_path,
                    value=key,
                    validating_type=key_type,
                    permissive_typing=permissive_typing,
                    depth=depth + 1,
                )
                value_validated = self.__process(
                    key_path=f"{key_path}.{key_validated}",
                    value=val,
                    validating_type=value_type,
                    permissive_typing=permissive_typing,
                    depth=depth + 1,
                )
                processed[key_validated] = value_validated

            return processed
        elif type_origin == Union:
            final_value = None
            errors = []
            for arg in type_args:
                try:
                    final_value = self.__process(
                        key_path=key_path,
                        value=value,
                        validating_type=arg,
                        permissive_typing=permissive_typing,
                        depth=depth + 1,
                    )
                    if final_value is not None:
                        return final_value
                except ValueError as e:
                    errors.append(f"\t{str(e)}")
            raise ValueError(
                "\n".join(
                    [
                        f"Value for '{key_path}' is invalid for union {repr_type(validating_type)}:"
                    ]
                    + errors
                )
            )
        elif type_origin == Literal:
            if value in type_args:
                return value
            else:
                raise ValueError(
                    f"Value for '{key_path}' is invalid for {repr_type(validating_type)}: '{value}'"
                )
        elif is_dataclass(validating_type):
            if isinstance(value, validating_type):
                # Do not validate further
                return value

            raw = value
            if not isinstance(raw, dict):
                raise ValueError(
                    f"Value provided for deserializable class {validating_type} at '{key_path}' is not a dictionary."
                )
            raw = value.copy()
            kwargs_dict = {}
            for current_field in fields(validating_type):
                key = current_field.name
                subtype: Type[Any] = current_field.type  # type: ignore
                explicitly_specified = False
                if key in raw:
                    explicitly_specified = True
                field_value = raw.get(key)
                field_default = None
                if (
                    current_field.default is not None
                    and current_field.default != MISSING
                ):
                    field_default = current_field.default
                if current_field.default_factory != MISSING:
                    field_default = current_field.default_factory()
                value__processed = self.__process(
                    key_path=f"{key_path}.{key}",
                    value=field_value,
                    explicitly_specified=explicitly_specified,
                    default=field_default,
                    validating_type=subtype,  # type: ignore
                    permissive_typing=permissive_typing,
                    depth=depth + 1,
                )
                kwargs_dict[key] = value__processed
                if explicitly_specified:
                    del raw[key]
            if len(raw):
                raise ValueError(
                    f"One or more keys unrecognized for dataclass {validating_type.__qualname__}: {' '.join(raw.keys())}"
                )
            return validating_type(**kwargs_dict)
        elif validating_type == Path:
            # Handle one-file globs
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            result = Path(value)
            result.validate(f"Path provided for variable '{key_path}' is invalid")
            return result
        elif validating_type is bool:
            if not permissive_typing and not isinstance(value, bool):
                raise ValueError(
                    f"Refusing to automatically convert '{value}' at '{key_path}' to a Boolean"
                )
            if value in ["1", "true", "True", 1, True]:
                return True
            elif value in ["0", "false", "False", 0, False]:
                return False
            else:
                raise ValueError(
                    f"Value provided for variable '{key_path}' of type {validating_type.__name__} is invalid: '{value}'"
                )
        elif issubclass(validating_type, Enum):
            if type(value) is validating_type:
                return value
            try:
                return validating_type[value]
            except KeyError:
                raise ValueError(
                    f"Variable provided for variable '{key_path}' of enumerated type {validating_type.__name__} is invalid: '{value}'"
                )
        elif issubclass(validating_type, str):
            if not is_string(value):
                raise ValueError(
                    f"Refusing to automatically convert value at '{key_path}' to a string"
                )
            return str(value)
        elif issubclass(validating_type, Decimal) or issubclass(validating_type, int):
            try:
                final = validating_type(value)
            except (InvalidOperation, TypeError):
                raise ValueError(
                    f"Value provided for variable '{key_path}' of type {validating_type.__name__} is invalid: '{value}'"
                )
            if not permissive_typing and not (
                isinstance(value, int)
                or isinstance(value, float)
                or isinstance(value, Decimal)
            ):
                raise ValueError(
                    f"Refusing to automatically convert value at '{key_path}' to a {validating_type.__name__}"
                )
            return final

        else:
            try:
                return validating_type(value)
            except ValueError as e:
                raise ValueError(
                    f"Value provided for variable '{key_path}' of type {validating_type.__name__} is invalid: '{value}' {e}"
                )
