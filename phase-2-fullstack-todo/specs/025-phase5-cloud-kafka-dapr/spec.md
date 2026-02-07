# Feature Specification: Phase 5 Advanced Cloud Deployment

**Feature Branch**: `025-phase5-cloud-kafka-dapr`
**Created**: 2026-01-25
**Status**: Ready for Planning

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Todo App to DigitalOcean Kubernetes (Priority: P1)
**User Journey**: DevOps engineer deploys the full-stack Todo app (frontend + backend + Neon DB) to DigitalOcean Kubernetes (DOKS BLR1) using Helm charts, verifies app is accessible via external URL, and confirms authentication/chat features work end-to-end.

**Why this priority**: Core deployment to cloud Kubernetes - foundation for all advanced features. Without this, no Phase 5 progress possible.

**Independent Test**: App loads at LoadBalancer IP, user can signup/login, create/view tasks via UI and chat, all data persists in Neon DB.

**Acceptance Scenarios**:
1. **Given** DOKS cluster active, **When** Helm install frontend/backend, **Then** pods running healthy, services get external IPs.
2. **Given** app deployed, **When** access frontend URL, **Then** dashboard loads, auth works.
3. **Given** tasks created via UI/chat, **When** refresh or restart pod, **Then** data persists.

### User Story 2 - Event-Driven Reminders & Recurring Tasks (Priority: P2)
**User Journey**: User creates task with due date/recurrence, system publishes Kafka event, consumer service (via Dapr Pub/Sub) triggers reminder or next instance, user receives notification (console/log for demo).

**Why this priority**: Core advanced feature - demonstrates Kafka/Dapr value. Builds directly on deployment.

**Independent Test**: Create task with due_date=now+1min, verify Kafka topic receives event, Dapr consumer processes it, log shows "Reminder sent".

**Acceptance Scenarios**:
1. **Given** task created with due_date, **When** due time reaches, **Then** Kafka "reminders" topic has event, Dapr job triggers notification.
2. **Given** recurring task completed, **When** completion event published, **Then** new instance auto-created with next date.
3. **Given** no Kafka/Dapr, **When** task created, **Then** events logged but not processed (fallback verification).

### User Story 3 - Priorities, Tags, Search/Filter/Sort (Priority: P3)
**User Journey**: User adds priorities/tags to tasks, searches/filters/sorts list, views enhanced dashboard with these features.

**Why this priority**: Completes intermediate features required by constitution. Enhances usability.

**Independent Test**: Create tasks with different priorities/tags, filter "high priority", search title, sort by date - results match expectations.

**Acceptance Scenarios**:
1. **Given** tasks with priorities/tags, **When** filter by "high" or tag "work", **Then** list shows matching tasks only.
2. **Given** task list, **When** search "meeting", **Then** matching title/desc tasks appear.
3. **Given** unfiltered list, **When** sort by priority/date, **Then** order correct.

### Edge Cases
- Cluster scaling: Add/remove node, app remains available.
- Kafka downtime: Fallback to DB queue/polling.
- Dapr sidecar failure: App graceful degradation (direct DB calls).
- High load: 100 concurrent users creating tasks (simulate).

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST deploy frontend/backend via Helm charts to DOKS BLR1 (1 node Basic).
- **FR-002**: System MUST publish task events (create/update/complete) to Kafka topics "task-events"/"reminders".
- **FR-003**: Dapr MUST handle Pub/Sub to Kafka, State (PostgreSQL), Secrets (K8s), Jobs (reminders).
- **FR-004**: Tasks MUST support recurring (daily/weekly), due_date, priority (low/medium/high/critical), tags (multi).
- **FR-005**: UI/API MUST support search (title/desc), filter (status/priority/tag), sort (date/priority/title).
- **FR-006**: Deployment MUST expose external URLs for frontend/backend, support stateless scaling.

### Key Entities
- **TaskEvent**: event_type, task_id, task_data, user_id, timestamp.
- **ReminderEvent**: task_id, title, due_at, remind_at, user_id.
- **Task**: + recurrence_rule, due_date, priority, tags[].

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: App fully deployed and accessible via external URL within 10 minutes post-cluster ready.
- **SC-002**: Task with due_date triggers Kafka event and Dapr-processed reminder (log verifiable).
- **SC-003**: Recurring task completion auto-creates next instance (DB verifiable).
- **SC-004**: Filter/search/sort returns correct results for 100 test tasks (100% accuracy).
- **SC-005**: Cluster scales to 2 nodes without downtime (kubectl verify).
- **SC-006**: 100% test coverage for new features (pytest/jest reports).
