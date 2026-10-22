# Installation

[Back to Orka](../README.md) · [Français](INSTALLATION.fr.md)

## Without Python: copy the skill folder

1. Download [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) and extract it. Use the skill ZIP, not the repository source archive.
2. Copy the complete extracted `orka` folder, including its references and guides, into your host's skills directory. Default user locations: `~/.agents/skills/orka/` for Codex, `~/.claude/skills/orka/` for Claude Code, or `~/.hermes/skills/orka/` for the default Hermes profile. Use the location configured by your host if it differs. Back up an existing installation before replacing it.
3. Start a new session if needed, select Orka and give it a mission. For Claude web/desktop, import the ZIP through its custom Skills interface instead of copying a local folder.

These steps do not execute the bundled Python scripts. You can keep those optional files without running them.

## Optional Python installer: Codex or Claude Code

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

The installer copies the whole skill folder, license and both getting-started guides, then displays the installed guide paths and a suggested first message. It makes no network calls, changes no assistant settings and refuses to overwrite an existing destination. Start a new session if the skill is not visible. In Codex, invoke `$orka`; in Claude Code, invoke `/orka`. ZIP imports include the guides as files; automatic opening depends on the host.

## Claude on the web or desktop

Download [orka.zip](https://github.com/AjinthAT/orka-skill/releases/latest/download/orka.zip) from the latest release, then upload it through Claude's custom Skills interface and enable it. Availability depends on your account and organization settings. Use the skill ZIP, **not** the repository source ZIP.

The archive contains `orka/SKILL.md` and its supporting files. See [Claude's installation guide](https://support.claude.com/en/articles/12512180-use-skills-in-claude) for the current interface. Cloud sessions provide their own tools and storage; installing a skill does not grant access to your local projects or enable parallel agents.

## Hermes Agent

The manual copy route above works for the default Hermes profile too. If you prefer the optional Python installer, run this from the cloned repository:

```sh
python3 install.py --destination "$HOME/.hermes/skills/orka"
```

Start a new Hermes session, then use `/orka`. If you use a different profile or `HERMES_HOME`, point `--destination` to that profile's `skills/orka` directory. This follows the [documented Hermes skills layout](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills); a complete Orka mission in Hermes has not yet been tested.

## Other assistants

Orka uses the open [Agent Skills format](https://agentskills.io/specification). For another host that supports it, copy the entire `.agents/skills/orka/` directory to that host's documented skills directory, or install to an explicit destination:

```sh
python3 install.py --destination /path/to/host/skills/orka
```

A model alone is not an installation target: the application running it must support skills or provide access to these instructions and their references. Apps without skill support can be given the files manually, but automatic discovery is unavailable. Compatibility with every AI application is not guaranteed.

## Updates and removal

### Check the installation first

Without Python, open the configured `orka` folder and check `SKILL.md`, `GUIDE.md`, `GUIDE.fr.md`, `LICENSE` and the archive's supporting files. Open local guide links. If something is missing, compare with a complete extraction of a known release and preserve local adaptations before replacing anything. Check Orka's selection in a new host session separately; file presence does not prove loading or available tools.

For an optional read-only report, use the diagnostic included since 0.5.0 from a reviewed copy:

```sh
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /path/to/installed/orka
python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /path/to/installed/orka --reference /path/to/known/orka --json
```

These examples run from the repository root; adapt the script path when using an installed copy. Python 3.10+ is required only for this optional tool. It makes no repairs, network calls or host launches. Code 0 means no detected anomaly in performed checks, 1 means a problem or difference, and 2 means invalid arguments. Without a complete valid reference, integrity remains unverified; matching a reference does not authenticate it. Host activation, models, tools and delegation remain unverified. See the [full procedure and supported formats](../.agents/skills/orka/references/diagnostic-installation.md), in French.

Back up any local adaptations before replacing an existing `orka` folder. The supplied installer refuses to overwrite it. To uninstall, remove only the installed skill folder; keep your mission outputs. The guides are included in the skill ZIP, but opening them automatically depends on the host.

Format and host references: [Agent Skills](https://agentskills.io/specification), [OpenAI](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills).
