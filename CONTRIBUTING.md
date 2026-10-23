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

For repeated-evaluation preparation and reporting, see [EVALUATIONS.md](docs/EVALUATIONS.md). The optional `tools/evaluer.py` uses only the standard library, freezes supplied inputs and imports observations without launching models. Its [regression suite](tests/test_evaluer.py) is included in the repository verifier; fabricated observations remain separate from real model executions.

The optional [file-tool MCP bridge](tools/raccorder_fichiers.py) is also repository-only and uses the standard library. Its [transport regressions](tests/test_raccorder_fichiers.py) run with temporary fake adapters, without Docker, network or models. The [independent connection probes](evals/raccordement-L4-2026-10-23/README.md) are software evidence, not L4 model runs or certification of a host's context isolation.

The separate [SDK–Inspect P0/P1 prototype](docs/PROTOTYPE-SDK-INSPECT.md) freezes new synthetic fixtures and runs only three file operations. Its portable contract tests are included in the verifier; the backend regressions require Linux `openat2`. The opt-in Docker suite runs them in the pinned, network-disabled Python image, without SDK installation or model calls. It requires the image to be cached first and never pulls it automatically. See its [acceptance record](docs/VALIDATION-PROTOTYPE-P01.md); this does not execute or alter L4.

Its optional [Claude Agent SDK adapter](docs/ADAPTATEUR-CLAUDE-SDK.md) has a separate dependency lock and opt-in offline tests of the real in-memory MCP catalogue, SDK configuration, and Docker binding. These tests do not start Claude Code or call a model. Neither SDK is required for ordinary repository verification or skill installation.

The [simulated Claude transport](tools/prototype_sdk_inspect/claude_simulated.py) also exercises the real SDK client and control protocol in memory, checking the serialized catalogue before every scripted generation. Its [regressions](tests/test_claude_simulated.py) include late catalogue drift and blocking a planned file write; the default CLI transport and network are trapped. See the [software acceptance record](docs/VALIDATION-TRANSPORT-CLAUDE-SIMULE.md). This simulation does not certify a real provider or Claude Code CLI run.

The optional [Inspect integration](docs/INSPECT-CLAUDE-SIMULE.md) runs that simulation with a custom solver and deterministic scorers of physical output and execution evidence. It has a separate combined lock, 11 frozen positive/negative scenarios and an explicit guard forbidding even mock model generation. Portable scorer tests join ordinary verification; framework and Docker tests are opt-in. See its [acceptance record](docs/VALIDATION-INSPECT-CLAUDE-SIMULE.md).

## Preserve evaluation records

Keep captured inputs, prompts, outputs and their manifests unchanged. Add new runs in a separate directory, with explicit criteria, source versions and available measurements. Preserve failed attempts and protocol deviations. The `evals/** -text` attribute preserves captured bytes even on CRLF-configured checkouts. Do not renormalize this directory. Do not reformat historical JSON or replace absolute paths inside raw captures merely to tidy them; portable indexes provide navigation without altering the originals.

Some historical recheck tools write verification files. Use a temporary copy when rechecking captured outputs. Replaying files is not a new model execution. Publish only data authorized for public distribution, with any redactions and new hashes identified.

## Build a distributable ZIP

```sh
python3 -B install.py --archive dist/orka.zip
```

The archive contains one `orka/` folder, both guides, all supporting resources and the MIT license. The builder refuses to overwrite an existing file; choose a new output path for a new build. Generated archives and caches stay outside commits.

Before a release, verify the final source and archive, align the version declared in `SKILL.md` with its `vX.Y.Z` tag, and check the tag's CI results. Preserve existing installations and local adaptations; publishing a release does not update personal skill folders automatically. Documentation-only repository maintenance does not require republishing an unchanged skill.
