{ pkgs, lib, config, inputs, ... }:

let
  pygameLibs = with pkgs; [
    libz
    libx11
    libxext
    libxcursor
    libxrandr
  ];
in
{
    packages = pygameLibs;

    languages.python = {
        enable = true;
        version = "3.14";
        lsp.enable = true;
        lsp.package = pkgs.python314Packages.python-lsp-server;
        venv.enable = true;
        uv = {
            enable = true;
            sync.enable = true;
        };
    };
    
    scripts= {
        format-check = {
            exec = ''
                ruff format --check .
            '';
            packages = [ pkgs.ruff ];
            description = "Run checks for the formatter";
        };
        format-fix = {
            exec = ''
                ruff format .
            '';
            packages = [ pkgs.ruff ];
            description = "Run auto-fixes for the formatter";
        };
        type-check = {
            exec = ''
                ty check
            '';
            packages = [ pkgs.ty ];
            description = "Run checks for type hints";
        };
        lint-check = {
            exec = ''
                ruff check .
            '';
            packages = [ pkgs.ruff ];
            description = "Run checks for the linter";
        };
        lint-fix = {
            exec = ''
                ruff check --fix .
            '';
            packages = [ pkgs.ruff ];
            description = "Run auto-fixes for the linter";
        };
    };
}
