# Contributing to Orka

Describe the observed problem, the intended result and the checks relevant to your change. Keep changes focused; distinguish documented procedures, executed agent work and future features. The [implementation overview](docs/IMPLEMENTATION.md) describes what is available, and [ECC-01](docs/LOT-ECC-01.md) tracks the current planned work.

## Repository layout

| Location | Purpose |
|---|---|
| `.agents/skills/orka/` | Self-contained skill distributed to users: instructions, guides, references, optional helpers and their tests |
| `docs/` | Installation guides, implementation overview and acceptance records |
| `evals/` | Preserved evaluation inputs, prompts, outputs, hashes and reviews; start with the [results index](evals/README.md) |
| `install.py` | Optional installer and portable ZIP builder |
| `tests/` | Distribution and installation checks |
| `tools/` | Repository maintenance checks |
| `dist/` | Generated ZIPs, ignored by Git; not source material |

Private product missions use `projets/<id>/`; cross-company missions use `entreprise/missions/<id>/`. Both are ignored. Application code belongs in its designated repository. Keep personal settings, credentials and private mission data out of public contributions.

## Check a change

Repository maintenance requires Python 3.10+ and the development dependency declared in [requirements-dev.txt](requirements-dev.txt). This does not change the skill's ordinary use or manual installation without Python. Use a local virtual environment if needed; `.venv/` is ignored.

From the repository root:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -B tools/verifier.py
```

The verifier checks metadata, maintained local links, all helper suites after installation in a temporary directory, and ZIP contents. It does not run models or write mission data. The [CI workflow](.github/workflows/verification.yml) runs it on Linux, macOS and Windows with Python 3.10 and 3.13. A configured matrix is distinct from the observed result of a particular run.

For changes to agent behavior, follow the [evaluation procedure](.agents/skills/orka/references/evaluation-agents.md). Software checks do not establish better model behavior, lower costs or complete host compatibility.

## Preserve evaluation records

Keep captured inputs, prompts, outputs and their manifests unchanged. Add new runs in a separate directory, with explicit criteria, source versions and available measurements. Preserve failed attempts and protocol deviations. Do not reformat historical JSON or replace absolute paths inside raw captures merely to tidy them; portable indexes provide navigation without altering the originals.

Some historical recheck tools write verification files. Use a temporary copy when rechecking captured outputs. Replaying files is not a new model execution. Publish only data authorized for public distribution, with any redactions and new hashes identified.

## Build a distributable ZIP

```sh
python3 -B install.py --archive dist/orka.zip
```

The archive contains one `orka/` folder, both guides, all supporting resources and the MIT license. The builder refuses to overwrite an existing file; choose a new output path for a new build. Generated archives and caches stay outside commits.

Before a release, verify the final source and archive, align the version declared in `SKILL.md` with its `vX.Y.Z` tag, and check the tag's CI results. Preserve existing installations and local adaptations; publishing a release does not update personal skill folders automatically. Documentation-only repository maintenance does not require republishing an unchanged skill.
