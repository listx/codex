let
  # Nixpkgs snapshot.
  sources = import ./package/nix/sources.nix;
  # The final "pkgs" attribute with all the bells and whistles of our overlays.
  pkgs = import sources.nixpkgs {};
  # This minimalist latex setup is adapted from https://nixos.wiki/wiki/TexLive.
  tex_for_orgmode = (pkgs.texlive.combine {
    # Start with scheme-basic.
    inherit (pkgs.texlive) scheme-basic
      # Add in additional TeX packages (think CTAN package names).
      wrapfig amsmath ulem hyperref capt-of

      # TikZ.
      pgf
      xkeyval
      fontspec
      tikz-qtree

      # Source Sans Pro font.
      sourcesanspro
      # Source Code Pro font.
      sourcecodepro
      ;
  });

in

# This is our development shell.
pkgs.mkShell ({
  buildInputs = [
    # Tangling and weaving for Literate Programming.
    pkgs.emacs29-nox

    # Diagrams.
    pkgs.inkscape
    pkgs.pdf2svg
    tex_for_orgmode

    # Misc
    pkgs.git
    pkgs.less

    # Update deps (bootstrap).
    pkgs.niv
    pkgs.nix
    pkgs.cacert

    # Spell checking.
    pkgs.typos

    # Link checker.
    pkgs.lychee

    # Python testing and linting.
    pkgs.python3Packages.hypothesis
    pkgs.python3Packages.mypy
    pkgs.ruff
  ];
})
