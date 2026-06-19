# SPDX-License-Identifier: MIT
# Copyright (c) 2025 CACE Contributors
# Copyright (c) 2023-2024 UmbraLogic Technologies LLC
{
  lib,
  git,
  zsh,
  delta,
  gtkwave,
  coreutils,
  graphviz,
  python3,
  devshell,
  extra-packages ? [ ],
  extra-python-packages ? ps: [ ],
  extra-env ? [ ],
  include-cace ? true,
}:
let
  cace = python3.pkgs.cace;
  cace-env = (
    python3.withPackages (
      pp:
      (
        if include-cace then
          ([ cace ])
        else
          (cace.propagatedBuildInputs)
      )
      ++ extra-python-packages pp
    )
  );
  cace-env-sitepackages = "${cace-env}/${cace-env.sitePackages}";
  prompt = ''\[\033[1;32m\][nix-shell:\w]\$\[\033[0m\] '';
  packages = [
    cace-env

    # Conveniences
    git
    zsh
    delta
    gtkwave
    coreutils
    graphviz
  ]
  ++ extra-packages
  ++ cace.includedTools;
in
devshell.mkShell {
  devshell.packages = packages;
  env = [
    {
      name = "NIX_PYTHONPATH";
      value = "${cace-env-sitepackages}";
    }
  ]
  ++ extra-env;
  devshell.interactive.PS1 = {
    text = ''PS1="${prompt}"'';
  };
  motd = "";
}
