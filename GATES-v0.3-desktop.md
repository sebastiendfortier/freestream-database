# Gates: freestream-database v0.3 desktop CI

OWNS: .github/workflows/build-windows.yml, scripts/verify_msi_ci.py, GATES-v0.3-desktop.md

Scope: Windows MSI GitHub Actions workflow succeeded on v0.3.0 tag

- [ ] G1: MSI CI workflow green with artifact
  CHECK: /bin/sh -c 'cd /home/slyfox/Documents/freestream-database && pixi run python scripts/verify_msi_ci.py'
  EXPECT: MSI_CI_OK
  EVIDENCE: pending
