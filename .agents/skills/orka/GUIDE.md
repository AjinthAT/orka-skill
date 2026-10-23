# Getting started with Orka

[Guide français](GUIDE.fr.md)

Orka coordinates an AI team around your project: clarifying an idea, researching a market, preparing marketing, coordinating development or reviewing results. You give it a mission; Orka selects useful perspectives, checks accessible evidence and delivers a result with its limits and a recommended next step. It does not launch every available role for every task.

**You can start without Python.** The core skill is Markdown: your assistant reads the instructions and uses its own tools. Copying the complete `orka` folder or importing its ZIP into a compatible host is enough for manual installation. Available features still depend on your assistant; installing Orka does not automatically add browsing or subagents.

| Use | Python |
|---|---|
| Read the skill, clarify, research, write and coordinate through host tools | Not required by Orka |
| Install with the supplied `install.py` script | Python 3.10+, optional when installing manually |
| Use the request preparer, SQLite register or local report | Python 3.10+, only when those checks are useful |
| Maintain and test the Orka repository | Python and development dependencies, outside ordinary use |

Start with mission documents. The register helps when coordinators share reservations, attempts must persist or versions need checking after an interruption; the preparer makes requests repeatable and the report summarizes supplied measurements. They are not needed for every mission and do not launch models. Your own project's requirements remain separate from the skill's.

## 1. Open Orka

You can check an installation **without Python**: open the configured `orka` folder, check `SKILL.md`, both guides, the license and the archive resources; follow local links, then separately check that Orka can be selected in a new host session. Keep any local adaptations before replacing files. The optional [diagnostic script](scripts/diagnostiquer.py) requires Python 3.10+, reads only the explicit skill/reference folders and never repairs them or launches the host. From a reviewed repository, run `python3 -B .agents/skills/orka/scripts/diagnostiquer.py --skill-dir /path/to/orka`; add `--reference /path/to/known/orka --json` for a comparison. Without a valid reference, integrity remains unverified; host activation and capabilities always remain unverified. See the [detailed procedure and format limits](references/diagnostic-installation.md), in French. No automatic check is required before each mission.

Select Orka through your assistant's skills mechanism. The entry points documented in the repository are `$orka` for Codex and `/orka` for Claude Code or Hermes; on another interface, ask the assistant to use Orka. Start a new session if the skill is not visible yet.

For a guided start, select the skill and copy this message:

```text
Orka, briefly explain how you work and help me choose a first mission for my project. Use the information already available and ask only for what is missing to get started.
```

If you have already provided a concrete assignment, Orka starts that work directly. You can request this guide at any time; reading it is not a prerequisite for each project.

For RH profiles and request preparation, choose the [Codex](references/modeles-effort.md) or [Claude Code/Agent SDK](references/modeles-effort-claude.md) reference. The SQLite registry currently uses the Codex format; Claude uses document-based tracking.

## 2. Give it a useful assignment

Share what you know: the project or problem, the result you want, the working folder and material constraints. Add audience, country, deadline or budget when known and relevant. An early idea is enough to start clarification; Orka should distinguish your choices, verified facts and hypotheses.

If a decisive input is missing, Orka requests the specific source or excerpt needed and records its provenance, version and effect on the result. The default limit is three context requests per task, carried across retries, unless the assignment explicitly sets another limit. When access or evidence is missing, it returns useful partial work and explains what remains unknown. Complete inputs need no extra question. This [progressive context protocol](references/prompting-agents.md#compléter-le-contexte-par-passes-bornées) and its [compact tracking example](references/modeles.md#suivi-des-compléments-de-contexte) use ordinary documents, without Python; full instructions are in French.

Pick the prompt that fits your need. Examples referring to an idea or folder assume you have already described it or made it accessible.

**Clarify an idea:**

```text
Orka, revisit the idea I just described. Help me clarify the problem, users, buyer and desired outcome. Preserve my ambition, verify accessible facts and ask the few questions that could change the next decision.
```

**Start a study:**

```text
Orka, study this project: customer need, alternatives and competitors, feasibility, adoption and economic assumptions. Use relevant specialists if delegation is available and authorized. Deliver a decision summary with dated sources, unknowns and a proportionate next validation test.
```

**Prepare marketing:**

```text
Orka, use the current project folder to prepare positioning, messaging and a launch plan. Check claims against the product that is actually available and deliver content for review.
```

**Develop an agreed feature:**

```text
Orka, implement the feature we defined in the designated repository. Reuse the acceptance criteria, coordinate the necessary work, verify the result and update the relevant documentation. Ask for the repository or criteria if they are not accessible.
```

**Resume a project:**

```text
Orka, resume the current project. Read its status, summary and decisions, check what remains valid and continue the authorized work. Identify missing information and propose the next useful decision.
```

## 3. Read the result and use the next prompt

Start with the summary: result, evidence, unknowns and the decision needed. Follow the linked files for detail. A small mission can use one combined deliverable.

Orka ends mission responses with **“Next prompt to copy”**, offering one suggestion in your language based on the project's actual state. Copy it if you want to take that step, or edit it. A suggestion does not execute the next phase or replace your decision. Orka should finish the work already requested before offering a continuation; when blocked, the prompt helps resolve the blocker.

You can request “only the deliverable” or “no next prompt” for a particular response. If there is no useful immediate follow-up, Orka suggests resuming when new feedback arrives rather than inventing work.

## 4. Adjust the team and resources

You can ask for a small team, a concise response, explicit objections or a particular model. Orka matches role, context and effort to the task within the host's capabilities. Requested and observed settings remain distinct.

Tokens and costs are known only when measurements are available. The [local agent report](references/bilan-agents.md) summarizes supplied records; it does not collect telemetry. If subagents are unavailable or unauthorized, Orka applies the useful perspectives sequentially and says so.

For repeated comparisons, the [evaluation procedure](references/evaluation-agents.md#préparer-et-relire-des-répétitions), in French, keeps every repetition and its criteria, including failures and unknowns. It works through ordinary documents without Python. An optional preparation/reporting tool is available in the source repository for maintenance; it is not in the installed ZIP and never launches models. Preparing a campaign does not authorize its execution.

## 5. Keep control of the project

A study does not establish willingness to buy or authorize a launch. Your request can authorize implementation; sending messages, spending, publishing or deploying requires instructions covering that action. Existing authorization remains valid within its scope.

Installation adds the skill files, including this guide. It starts no agents or permanent service. Keep your mission folders so work can resume; installing the skill does not back them up automatically.

For more detail, ask Orka for the relevant workflow: [experiments](references/experiences-apprentissage.md), [names and domains](references/noms-domaines.md) or [AI resources](references/ressources-agents.md). You do not need to read every reference to start.
