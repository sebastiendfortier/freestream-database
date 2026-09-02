# Gates: freestream-database v0.2 desktop

OWNS: pyproject.toml, .github/workflows/build-windows.yml, GATES-v0.2-desktop.md

Scope: Windows MSI CI workflow present and valid

- [x] G1: build-windows workflow exists
  CHECK: /bin/sh -c 'test -f /home/slyfox/Documents/freestream-database/.github/workflows/build-windows.yml && python3 -c "import pathlib; t=pathlib.Path(\"/home/slyfox/Documents/freestream-database/.github/workflows/build-windows.yml\").read_text(); assert \"pyappdist\" in t; print(\"WINDOWS_CI_OK\")"'
  EXPECT: WINDOWS_CI_OK
  EVIDENCE: shell=/bin/sh; cwd=/home/slyfox/Documents/freestream-resolver; exit=0; path=c2fddda5c8ee/25; out=WINDOWS_CI_OK
