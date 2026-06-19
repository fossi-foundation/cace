# SPDX-License-Identifier: MIT
# Copyright 2025 CACE Contributors
# Copyright (c) 2023-2025 UmbraLogic Technologies LLC
{
  description = "open-source framework for automatic circuit characterization";

  inputs = {
    nix-eda.url = "github:fossi-foundation/nix-eda/6.24.0";
    ciel.url = "github:fossi-foundation/ciel/2.5.0";
    devshell.url = "github:numtide/devshell";
    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1.tar.gz";
  };

  inputs.ciel.inputs.nix-eda.follows = "nix-eda";
  inputs.devshell.inputs.nixpkgs.follows = "nix-eda/nixpkgs";

  outputs =
    {
      self,
      nix-eda,
      ciel,
      devshell,
      ...
    }:
    let
      nixpkgs = nix-eda.inputs.nixpkgs;
      lib = nixpkgs.lib;
    in
    {
      # Common
      overlays = {
        default = lib.composeManyExtensions [
          (ciel.overlays.default)
          (
            pkgs': pkgs:
            let
              callPackage = lib.callPackageWith pkgs';
            in
            {
              colab-env = callPackage ./nix/colab-env.nix { };
            }
          )
          (nix-eda.composePythonOverlay (
            pkgs': pkgs: pypkgs': pypkgs:
            let
              callPythonPackage = lib.callPackageWith (pkgs' // pypkgs');
            in
            {
              mpld3 = callPythonPackage ./nix/mpld3.nix { };
              cace = callPythonPackage ./default.nix {
                flake = self;
              };
            }
          ))
          (
            pkgs': pkgs:
            let
              callPackage = lib.callPackageWith pkgs';
            in
            {
              cace-shell = callPackage ./nix/create-shell.nix { };
            }
            // lib.optionalAttrs pkgs.stdenv.isLinux {
              cace-docker = callPackage ./nix/docker.nix {
                createDockerImage = nix-eda.createDockerImage;
                cace = pkgs'.python3.pkgs.cace;
              };
            }
          )
        ];
      };

      # Packages
      legacyPackages = nix-eda.forAllSystems (
        system:
        import nix-eda.inputs.nixpkgs {
          inherit system;
          overlays = [
            devshell.overlays.default
            nix-eda.overlays.default
            self.overlays.default
          ];
        }
      );

      packages = nix-eda.forAllSystems (
        system:
        let
          pkgs = self.legacyPackages."${system}";
        in
        {
          inherit (pkgs) colab-env;
          inherit (pkgs.python3.pkgs) cace;
          default = pkgs.python3.pkgs.cace;
        }
        // lib.optionalAttrs pkgs.stdenv.isLinux {
          inherit (pkgs) cace-docker;
        }
      );

      # Development Shells
      devShells = nix-eda.forAllSystems (
        system:
        let
          pkgs = self.legacyPackages."${system}";
          callPackage = lib.callPackageWith pkgs;
        in
        {
          # These devShells are rather unorthodox for Nix devShells in that they
          # include the package itself. For a proper devShell, try .#dev.
          default = pkgs.cace-shell;
          notebook = pkgs.cace-shell.override ({
            extra-packages = with pkgs; [
              jupyter
            ];
            extra-python-packages =
              ps: with ps; [
                pandas
              ];
          });
          # Normal devShells
          dev = pkgs.cace-shell.override ({
            extra-python-packages =
              ps: with ps; [
                setuptools
                build
                twine
                black
              ];
            include-cace = false;
          });
          docs = pkgs.cace-shell.override ({
            extra-python-packages = 
              ps: with ps; [
                sphinx
                myst-parser
                furo
                sphinx-autobuild
              ];
            include-cace = false;
          });
        }
      );
    };
}
