default: install

alias c := check

check: && format
    yamllint .
    ruff check --fix .
    # pyright --warnings
    asciidoctor **/*.adoc
    lychee --cache **/*.html
    nix flake check

alias f := format
alias fmt := format

format:
    treefmt

init-dev: && sync
    [ -d .venv ] || python -m venv .venv
    .venv/bin/python -m pip install pip-tools
    .venv/bin/python -m pip install --requirement requirements-dev.txt

run:
    #!/usr/bin/env nu
    ^python driverbrainz.py

sync:
    source .venv/bin/activate && pip-sync --python-executable .venv/bin/python requirements-dev.txt

alias u := update
alias up := update

update:
    nix run ".#update-nix-direnv"
    nix run ".#update-nixos-release"
    nix flake update
    source .venv/bin/activate && pip-compile requirements-dev.in
