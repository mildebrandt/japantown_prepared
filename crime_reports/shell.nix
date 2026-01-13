# shell.nix
let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2026-01-12. Check for new commits at https://status.nixos.org.
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/d03088749a110d52a4739348f39a63f84bb0be14.tar.gz") {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      # select Python packages here
      pandas
      requests
      tabulate
    ]))
  ];
}
