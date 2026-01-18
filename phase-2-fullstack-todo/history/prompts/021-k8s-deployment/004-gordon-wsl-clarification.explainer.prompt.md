---
id: 2
title: Clarification on Gordon AI WSL Accessibility
stage: explainer
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: 021-k8s-deployment
branch: 021-k8s-deployment
user: huzaifasys
command: /sp.clarify
labels: [gordon, wsl2, docker, clarification]
links:
  spec: specs/021-k8s-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

but gordon only cmd or ps ma use ho sakta not in wsl so how can you do that ?

## Response snapshot

Addressed the technical limitation where Gordon AI (Docker AI) is only available on the Windows host and not inside WSL2. Proposed a "Manual Bridge" strategy where the agent provides prompts for the user to run in PowerShell, ensuring the output remains AI-generated and compliant with Spec-Driven Development rules.

## Outcome

- ✅ Impact: Medium (Resolved a deployment blocker)
- 🔁 Next prompts: Wait for user selection then update spec/plan.
- 🧠 Reflection: Important to account for host vs. guest OS tool availability in monorepo setups.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Next experiment: none
