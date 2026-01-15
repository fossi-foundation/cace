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

registered_tools = {}


def register_parameter(name=None):
    def inner(cls):
        registered_tools[name] = cls
        return cls

    return inner

def register_tool(name=None):
    def inner(cls):
        if name:
            registered_tools[name] = cls
        else:
            registered_tools[cls.name] = cls
        return cls

    return inner

def get_tools(category=None):
    tools = []

    if category:
        for tool in registered_tools.values:
            if tool.name.split('.')[0] == category:
                tools += tool
    else:
        tools = registered_tools

    return tools

def find_tool(name):
    if name in registered_tools:
        return registered_tools[name]
    
    for tool in registered_tools.values:
        if tool.name == name:
            return tool
    
    return None
