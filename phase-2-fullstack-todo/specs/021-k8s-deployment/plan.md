# Implementation Plan: Phase 4 Local Kubernetes Deployment

**Branch**: `021-k8s-deployment` | **Date**: 2026-01-08 | **Spec**: [specs/021-k8s-deployment/spec.md](spec.md)
**Input**: Feature specification from `/specs/021-k8s-deployment/spec.md`

## Summary
Deploy the Phase III Todo Chatbot to a local Kubernetes cluster using Minikube and Helm charts. The deployment process will be fully automated using AI-assisted tools: Gordon (Docker AI) for containerization, kubectl-ai for orchestration, and kagent for observability.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/Next.js 16+ (Frontend)
**Primary Dependencies**: Docker Desktop, Minikube, Helm, kubectl-ai, kagent
**Storage**: Neon Serverless PostgreSQL (External), or local PostgreSQL pod (NEEDS CLARIFICATION)
**Testing**: kagent health reports, `kubectl get pods` verification
**Target Platform**: Local Kubernetes (Minikube with Docker driver)
**Project Type**: Cloud-native web application deployment
**Performance Goals**: Pod readiness < 60s, Auto-scaling capability (simulated)
**Constraints**: Zero manual manifest editing, 100% AI-generated infra code
**Scale/Scope**: 2 services (frontend, backend), 1 database connection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (SDD)**: ✅ All infra artifacts will be generated via AI tools.
- **Principle VII (Stateless)**: ✅ Kubernetes pods will remain stateless; DB state is persisted externally.
- **Phase IV Requirement**: ✅ Using Gordon, Minikube, Helm, kubectl-ai, and kagent as mandated.

## Project Structure

### Documentation (this feature)

```text
specs/021-k8s-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # N/A (Infra-focused)
├── quickstart.md        # Deployment instructions
├── contracts/           # Kubernetes service definitions
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
infrastructure/
├── docker/
│   ├── frontend.Dockerfile
│   └── backend.Dockerfile
└── helm/
    └── taskwave/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

**Structure Decision**: Infrastructure artifacts will be stored in a new `infrastructure/` directory at the root to maintain clean separation from application logic.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New `infrastructure/` dir | Standard K8s practice for monorepos | Mixing YAMLs in app folders causes clutter |

## Phase 0: Outline & Research

1. **Research Task**: "Identify optimal multi-stage Docker build patterns for Next.js 16 and FastAPI 0.100+ using Gordon AI."
2. **Research Task**: "Determine how to handle Neon DB secrets in Helm charts without hardcoding (Secrets vs ConfigMaps)."
3. **Research Task**: "Verify kubectl-ai command syntax for deploying Helm-packaged applications."

## Phase 1: Design & Contracts

1. **Quickstart.md**: Define the exact sequence of AI commands to go from source code to running pods.
2. **Contracts**: Define the K8s Service interfaces (NodePort vs LoadBalancer for Minikube).
3. **Agent Context**: Run `.specify/scripts/bash/update-agent-context.sh` to include Docker/K8s skills.
