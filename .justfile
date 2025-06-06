default: run

alias c := check

check: && format
    yamllint .
    ruff check --fix .
    mypy
    pyright --warnings
    asciidoctor **/*.adoc
    lychee --cache **/*.html
    nix flake check

alias f := format
alias fmt := format

format:
    treefmt

run:
    #!/usr/bin/env nu
    ^python driverbrainz.py

alias u := update
alias up := update

update:
    nix run ".#update-nix-direnv"
    nix run ".#update-nixos-release"
    nix flake update
