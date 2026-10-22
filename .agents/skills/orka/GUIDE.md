# Getting started with Orka

[Guide français](GUIDE.fr.md)

Orka coordinates an AI team around your project: clarifying an idea, researching a market, preparing marketing, coordinating development or reviewing results. You give it a mission; Orka selects useful perspectives, checks accessible evidence and delivers a result with its limits and a recommended next step. It does not launch every available role for every task.

## 1. Open Orka

Select Orka through your assistant's skills mechanism. The entry points documented in the repository are `$orka` for Codex and `/orka` for Claude Code or Hermes; on another interface, ask the assistant to use Orka. Start a new session if the skill is not visible yet.

For a guided start, select the skill and copy this message:

```text
Orka, briefly explain how you work and help me choose a first mission for my project. Use the information already available and ask only for what is missing to get started.
```

If you have already provided a concrete assignment, Orka starts that work directly. You can request this guide at any time; reading it is not a prerequisite for each project.

## 2. Give it a useful assignment

Share what you know: the project or problem, the result you want, the working folder and material constraints. Add audience, country, deadline or budget when known and relevant. An early idea is enough to start clarification; Orka should distinguish your choices, verified facts and hypotheses.

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

## 5. Keep control of the project

A study does not establish willingness to buy or authorize a launch. Your request can authorize implementation; sending messages, spending, publishing or deploying requires instructions covering that action. Existing authorization remains valid within its scope.

Installation adds the skill files, including this guide. It starts no agents or permanent service. Keep your mission folders so work can resume; installing the skill does not back them up automatically.

For more detail, ask Orka for the relevant workflow: [experiments](references/experiences-apprentissage.md), [names and domains](references/noms-domaines.md) or [AI resources](references/ressources-agents.md). You do not need to read every reference to start.
