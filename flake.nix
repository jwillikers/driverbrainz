{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nix-update-scripts = {
      url = "github:jwillikers/nix-update-scripts";
      inputs = {
        flake-utils.follows = "flake-utils";
        nixpkgs.follows = "nixpkgs";
        pre-commit-hooks.follows = "pre-commit-hooks";
        treefmt-nix.follows = "treefmt-nix";
      };
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs = {
        nixpkgs.follows = "nixpkgs";
      };
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs =
    {
      self,
      nix-update-scripts,
      nixpkgs,
      flake-utils,
      pre-commit-hooks,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = import ./overlays { };
        pkgs = import nixpkgs {
          inherit system overlays;
        };
        pre-commit = pre-commit-hooks.lib.${system}.run (
          import ./pre-commit-hooks.nix { inherit pkgs treefmtEval; }
        );
        treefmtEval = treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
      in
      with pkgs;
      {
        apps = {
          inherit (nix-update-scripts.apps.${system}) update-nix-direnv update-nixos-release;
        };
        devShells.default = mkShell {
          inherit (pre-commit) shellHook;
          nativeBuildInputs =
            with pkgs;
            [
              asciidoctor
              firefox
              fish
              geckodriver
              just
              lychee
              nushell
              pyright
              python3Packages.platformdirs
              python3Packages.pykakasi
              python3Packages.pytest
              python3Packages.python
              python3Packages.requests
              python3Packages.selenium
              python3Packages.types-requests
              python3Packages.wikitextparser
              treefmtEval.config.build.wrapper
            ]
            ++ builtins.attrValues treefmtEval.config.build.programs
            ++ pre-commit.enabledPackages;
        };
        packages = {
          default = self.packages.${system}.driverbrainz;
          driverbrainz = callPackage ./package.nix { };
        };
        # Building the package runs the unit tests.
        checks = {
          inherit (self.packages.${system}) driverbrainz;
        };
        formatter = treefmtEval.config.build.wrapper;
      }
    );
}
