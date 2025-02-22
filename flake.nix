{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {nixpkgs, ...}: let
    supportedSystems = ["x86_64-linux"];

    forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

    nixpkgsFor = forAllSystems (system:
      import nixpkgs {
        inherit system;
      });
  in {
    devShells = forAllSystems (system: let
      pkgs = nixpkgsFor.${system};
    in {
      default = pkgs.mkShell {
        packages = [
          pkgs.pnpm
          pkgs.nodejs
          pkgs.prettierd
          pkgs.vscode-langservers-extracted
          pkgs.nodePackages.typescript-language-server
          pkgs.tailwindcss-language-server
        ];
      };
    });
  };
}
