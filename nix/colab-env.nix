# SPDX-License-Identifier: MIT
# Copyright (c) 2025 CACE Contributors
# Copyright (c) 2023-2024 UmbraLogic Technologies LLC
{
  system,
  python3,
  symlinkJoin,
}:
symlinkJoin {
  name = "cace-colab-env";
  paths = python3.pkgs.cace.includedTools;
}
