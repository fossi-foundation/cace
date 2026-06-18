# SPDX-License-Identifier: MIT
# Copyright (c) 2025 CACE Contributors
# Copyright (c) 2023-2024 UmbraLogic Technologies LLC
{
  createDockerImage,
  dockerTools,
  stdenv,
  pkgs,
  lib,
  python3,
  cace,
  git,
  zsh,
  silver-searcher,
  coreutils,
}:
let
  cace-env = python3.withPackages (ps: with ps; [ cace ]);
  cace-env-sitepackages = "${cace-env}/${cace-env.sitePackages}";
  cace-env-bin = "${cace-env}/bin";
in
createDockerImage {
  inherit pkgs;
  inherit lib;
  name = "cace";
  tag = "tmp-${stdenv.hostPlatform.system}";
  extraPkgs = with dockerTools; [
    git
    zsh
    silver-searcher

    cace-env
  ];
  nixConf = {
    extra-experimental-features = "nix-command flakes repl-flake";
  };
  maxLayers = 2;
  channelURL = "https://nixos.org/channels/nixos-23.11";

  image-created = "now";
  image-extraCommands = ''
    mkdir -p ./etc
    mkdir -p ./tmp
    chmod 1777 ./tmp

    cat <<HEREDOC > ./etc/zshrc
    autoload -U compinit && compinit
    autoload -U promptinit && promptinit && prompt suse && setopt prompt_sp
    autoload -U colors && colors

    export PS1=$'%{\033[31m%}CACE Container (${cace.version})%{\033[0m%}:%{\033[32m%}%~%{\033[0m%}%% ';
    HEREDOC
  '';
  image-config-cmd = [ "${zsh}/bin/zsh" ];
  image-config-extra-env = [
    "LANG=C.UTF-8"
    "LC_ALL=C.UTF-8"
    "LC_CTYPE=C.UTF-8"
    "EDITOR=nvim"
    "NIX_PYTHONPATH=/host_librelane:${cace-env-sitepackages}"
    "TMPDIR=/tmp"
  ];
  image-config-extra-path = [
    "${cace-env-bin}"
    "${cace.computed_PATH}"
  ];
}
