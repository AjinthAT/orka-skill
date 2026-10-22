# Orka

**Give your AI assistant a coordinated business team.**

[Français](README.fr.md) · [Download Orka](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) · [Skill instructions](.agents/skills/orka/SKILL.md)

Orka is an Agent Skill for coordinating specialists across strategy, market research, marketing, sales, product, development, quality, operations, finance, HR and customer support. A coordinator assigns focused tasks, brings together useful objections, checks evidence and maintains shared deliverables.

**28 roles · 8 teams · 9 workflows · MIT license**

Orka provides instructions, templates and optional local Python tools. Your assistant supplies the models and execution tools. Installing Orka does not start agents, provision services or require an API key. Model use remains subject to your assistant's plan and costs.

## Install

### Codex or Claude Code

Download the [source ZIP](https://github.com/AjinthAT/orka-skill/archive/refs/heads/main.zip) and extract it, or clone the repository:

```sh
git clone https://github.com/AjinthAT/orka-skill.git
cd orka-skill
```

With Python 3.10 or later, run **one** command for your assistant:

```sh
# Codex: install for your user
python3 install.py --agent codex

# Claude Code: install for your user
python3 install.py --agent claude
```

On Windows, use `py -3` instead of `python3` if needed. No third-party Python packages are required.

| Assistant | User installation | Project installation |
|---|---|---|
| Codex | `~/.agents/skills/orka/` | `<project>/.agents/skills/orka/` |
| Claude Code | `~/.claude/skills/orka/` | `<project>/.claude/skills/orka/` |

For a project installation, add `--project /path/to/existing-project` to the selected command. Without that flag, installation is for your user, even when you run it inside a project.

The installer copies the whole skill folder and license. It makes no network calls, changes no assistant settings and refuses to overwrite an existing destination. Start a new session if the skill is not visible. In Codex, invoke `$orka`; in Claude Code, invoke `/orka`.

### Claude on the web or desktop

Download [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) from the latest release, then upload it through Claude's custom Skills interface and enable it. Availability depends on your account and organization settings. Use the skill ZIP, **not** the repository source ZIP.

The archive contains `orka/SKILL.md` and its supporting files. See [Claude's installation guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for the current interface. Cloud sessions provide their own tools and storage; installing a skill does not grant access to your local projects or enable parallel agents.

### Other assistants

Orka uses the open [Agent Skills format](https://agentskills.io/specification). For another host that supports it, copy the entire `.agents/skills/orka/` directory to that host's documented skills directory, or install to an explicit destination:

```sh
python3 install.py --destination /path/to/host/skills/orka
```

A model alone is not an installation target: the application running it must support skills or provide access to these instructions and their references. Apps without skill support can be given the files manually, but automatic discovery is unavailable. Compatibility with every AI application is not guaranteed.

## Start a mission

After invoking Orka in your assistant, describe the result you want:

> Study an appointment-booking product for independent fitness coaches in France. Assess competitors, customer needs and pricing assumptions. Use specialist subagents if available and permitted, challenge the proposal, and save a decision brief with sources, uncertainties and the next validation test. Respond in English.

Or start with a specific department:

- “Prepare a launch marketing plan for my product, including positioning, channels and draft content.”
- “Coordinate implementation of this approved feature, with separate development and review deliverables.”
- “Review customer feedback and propose a prioritized improvement plan.”

Give the coordinator the project, expected output, relevant files and known constraints. A focused mission activates only the roles it needs. External communications, spending, publication and deployment require authorization covering the action.

## How it works

1. **Frame the mission:** identify scope, inputs, constraints and acceptance criteria.
2. **Assign the work:** select specialists, dependencies and separate outputs.
3. **Execute and challenge:** perform ready tasks, exchange relevant findings and resolve useful objections.
4. **Verify and deliver:** check evidence, accept the reviewed versions and record decisions and remaining uncertainty.

When authorized subagents are available, the coordinator can delegate. Otherwise it applies the specialist perspectives sequentially and states that limitation. It must not present simulated exchanges as independent agent work.

| Team | Responsibilities |
|---|---|
| Direction and strategy | Coordination, market research, competition, critical review |
| Marketing | Strategy, copywriting, SEO, social media, acquisition |
| Sales | Sales planning, prospecting, partnerships |
| Product and design | Product priorities, project management, UX/UI |
| Engineering | CTO, architecture, frontend, backend, security, QA, DevOps |
| Finance and administration | Budgets, economics, administrative tracking |
| Human resources | HR leadership, recruiting, onboarding, training |
| Customer relations | Support, adoption, retention |

The role catalogue does not require 28 agents to run simultaneously. The workflows cover market studies, marketing, sales, delivery, launch, customer relations, finance, HR and business steering.

## Compatibility and current limits

- **Portable instructions:** `SKILL.md`, roles, workflows and templates are shared across hosts. The detailed references are currently in French; Orka follows the user's requested output language.
- **Host-specific execution:** model selection, reasoning controls, browsing, delegation and file access depend on the host. The included model catalogue and JSON request preparer target Codex-style launch parameters; they do not configure Claude. Other hosts use their native settings and document-based tracking unless a compatible catalogue is configured.
- **Optional local tools:** a Python request preparer and SQLite supervision register support repeatable mandates, reservations, dependencies, attempts and artifact acceptance. The register uses the preparer and shares its catalogue constraints. Neither tool calls a model, launches or stops an agent, or runs continuously.
- **Validation scope:** local tests cover the helpers, installation and packaging. Codex, Claude Code and Claude upload paths follow their documented formats; this release has not undergone an end-to-end model evaluation on each host.

## Documentation

| Resource | Contents |
|---|---|
| [Skill entry point](.agents/skills/orka/SKILL.md) | Core coordination instructions and reference routing |
| [Teams and roles](.agents/skills/orka/references/roles.md) | The 28 specialist roles |
| [Business workflows](.agents/skills/orka/references/workflows-entreprise.md) | Department workflows and handoffs |
| [Market-study workflow](.agents/skills/orka/references/workflow-etude.md) | Research stages and decision criteria |
| [Agent orchestration](.agents/skills/orka/references/orchestration-agents.md) | Delegation, context and capacity |
| [Local supervision](.agents/skills/orka/references/supervision-locale.md) | Optional persistent register and its limits |
| [Model profiles](.agents/skills/orka/references/modeles-effort.md) | Codex reference settings and adaptation boundaries |
| [Mandates and prompts](.agents/skills/orka/references/prompting-agents.md) | Task contracts and the optional preparer |
| [Document templates](.agents/skills/orka/references/modeles.md) | Shared evidence, decisions and handoffs |
| [Implementation](docs/IMPLEMENTATION.md) | Implemented capabilities and future work |
| [Behavioral validation](.agents/skills/orka/references/validation.md) | Scenarios for evaluating the skill |

Product mission documents live under `projets/<id>/`; cross-company missions use `entreprise/missions/<id>/`. Application code stays in the designated development repository. Keep private mission data out of this public distribution repository; the optional local register defaults in the examples to the ignored `.orka/` directory.

## Development

From the repository root:

```sh
python3 -B .agents/skills/orka/scripts/test_preparer_agent.py
python3 -B .agents/skills/orka/scripts/test_superviser.py
python3 -B -m unittest discover -s tests
python3 install.py --archive dist/orka.zip
```

To update an installation, review the changes, back up any local modifications, remove the old installed `orka` folder and run the installer again. To uninstall, remove only the installed `orka` folder; this leaves mission outputs intact. The installer intentionally has no automatic overwrite mode.

Contributions are welcome through issues and pull requests. Describe the observed problem, keep changes focused, and include the relevant checks. Distinguish a documented procedure from a capability actually executed and verified.

## License and format references

[MIT](LICENSE). The release archive and installed copies include the license.

Installation locations and skill discovery: [OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills), [Claude Code's skills documentation](https://code.claude.com/docs/en/skills). Orka's team structure and workflows are this project's design, not features supplied by those platforms.
