# Tasks: Advanced Task Filtering and Search

**Feature**: Advanced Task Filtering and Search
**Branch**: `012-task-filtering-search`
**Created**: 2025-12-25
**Status**: Ready for Implementation

---

## Overview

This document breaks down the task filtering and search enhancement into atomic tasks organized by user story. Each user story represents an independently testable filtering capability.

**User Stories from Spec**:
- **US1 (P1)**: Search Tasks by Text
- **US2 (P1)**: Filter by Priority
- **US3 (P2)**: Filter by Tag
- **US4 (P2)**: Filter by Status
- **US5 (P2)**: Sort Tasks
- **US6 (P3)**: Combine Multiple Filters
- **US7 (P1)**: Paginate Results

---

## Implementation Strategy

### MVP Scope
**US1 + US7**: Text search + pagination
- Core search functionality
- Pagination for performance
- Delivers immediate value

### Incremental Delivery
1. **Iteration 1**: US1 + US7 (Search + Pagination)
2. **Iteration 2**: US2 + US4 (Priority + Status filters)
3. **Iteration 3**: US5 (Sorting)
4. **Iteration 4**: US3 (Tag filtering with JOIN)
5. **Iteration 5**: US6 (Combined filters)

### Parallel Opportunities
- US2 and US4 can be developed in parallel (independent filters)
- Tests can be written in parallel with implementation

---

## Phase 1: Setup & Prerequisites

**Goal**: Verify existing infrastructure and indexes

**Tasks**:

- [ ] T001 Verify Task model has indexed fields in backend/models.py (user_id, priority, completed, created_at, updated_at)
- [ ] T002 Verify TaskTag model has index on tag_name field in backend/models.py
- [ ] T003 Verify existing GET /users/{user_id}/tasks endpoint in backend/routes/tasks.py
- [ ] T004 Verify existing get_user_tasks function in backend/services/task_service.py

**Acceptance**: All prerequisites verified, ready for enhancement

---

## Phase 2: Foundational Components

**Goal**: Update schemas and prepare service layer for enhancements

**Tasks**:

- [ ] T005 [P] Update TaskListResponse schema in backend/schemas/task.py (add page: int and limit: int fields with descriptions)
- [ ] T006 [P] Add SortEnum in backend/schemas/task.py (values: created, title, priority, updated)
- [ ] T007 [P] Add StatusEnum in backend/schemas/task.py (values: pending, completed, all)

**Acceptance**: Schemas updated with pagination and filter enums

---

## Phase 3: US1 - Search Tasks by Text (P1)

**Story Goal**: Users can search tasks by entering text that matches title or description

**Independent Test**: Search for "meeting" returns only tasks with "meeting" in title/description

**Service Layer**:

- [ ] T008 [US1] Add search filter logic to get_user_tasks in backend/services/task_service.py (use or_() with Task.title.ilike() and Task.description.ilike() for case-insensitive partial matching)

**Integration Tests**:

- [ ] T009 [US1] Test search matches task title case-insensitive in backend/tests/test_task_filtering.py
- [ ] T010 [US1] Test search matches task description case-insensitive
- [ ] T011 [US1] Test search with no matches returns empty array with total=0
- [ ] T012 [US1] Test search with special characters (%, _, \) handled safely
- [ ] T013 [US1] Test empty search term returns all tasks

**Acceptance**: Text search functional, case-insensitive, handles edge cases

---

## Phase 4: US7 - Paginate Results (P1)

**Story Goal**: Users receive paginated results with metadata for large task lists

**Independent Test**: Request limit=20 and offset=0 returns first 20 tasks with total count

**Service Layer**:

- [ ] T014 [US7] Update get_user_tasks to execute separate count query before pagination in backend/services/task_service.py (use select(func.count()).select_from(query.subquery()))
- [ ] T015 [US7] Add limit capping logic in get_user_tasks (min(limit, 100))

**Route Layer**:

- [ ] T016 [US7] Update route handler to calculate page number in backend/routes/tasks.py (page = (offset // limit) + 1)
- [ ] T017 [US7] Update TaskListResponse return to include page and limit fields

**Integration Tests**:

- [ ] T018 [US7] Test pagination with default limit=20 and offset=0
- [ ] T019 [US7] Test pagination with custom limit and offset (second page)
- [ ] T020 [US7] Test limit > 100 is capped at 100
- [ ] T021 [US7] Test offset beyond total returns empty array
- [ ] T022 [US7] Test page number calculation correct for various offsets
- [ ] T023 [US7] Test total count reflects filtered results (not all tasks)

**Acceptance**: Pagination working, limit capped, page metadata correct

---

## Phase 5: US2 - Filter by Priority (P1)

**Story Goal**: Users can filter tasks by priority level

**Independent Test**: Filter by priority="high" returns only high-priority tasks

**Service Layer**:

- [ ] T024 [US2] Add priority filter logic to get_user_tasks (already exists, verify working correctly)

**Integration Tests**:

- [ ] T025 [US2] Test filter by priority="low" returns only low-priority tasks
- [ ] T026 [US2] Test filter by priority="high" returns only high-priority tasks
- [ ] T027 [US2] Test filter by priority="critical" returns only critical tasks
- [ ] T028 [US2] Test invalid priority value returns validation error

**Acceptance**: Priority filtering functional for all priority levels

---

## Phase 6: US4 - Filter by Status (P2)

**Story Goal**: Users can filter tasks by completion status

**Independent Test**: Filter by status="pending" returns only incomplete tasks

**Service Layer**:

- [ ] T029 [US4] Extend get_user_tasks to handle status parameter in backend/services/task_service.py (map pending→completed=false, completed→completed=true, all→no filter)

**Route Layer**:

- [ ] T030 [US4] Add status query parameter to route handler in backend/routes/tasks.py (Optional[StatusEnum])

**Integration Tests**:

- [ ] T031 [US4] Test filter by status="pending" returns only incomplete tasks
- [ ] T032 [US4] Test filter by status="completed" returns only completed tasks
- [ ] T033 [US4] Test filter by status="all" returns all tasks

**Acceptance**: Status filtering functional for pending/completed/all

---

## Phase 7: US5 - Sort Tasks (P2)

**Story Goal**: Users can sort filtered results by different criteria

**Independent Test**: Sort by created returns newest tasks first

**Service Layer**:

- [ ] T034 [US5] Add sort logic to get_user_tasks in backend/services/task_service.py (created→created_at.desc, title→title.asc, updated→updated_at.desc)
- [ ] T035 [US5] Implement priority sorting with CASE expression (critical=1, high=2, medium=3, low=4, then order_by case value)

**Route Layer**:

- [ ] T036 [US5] Add sort query parameter to route handler (Optional[SortEnum], default="created")

**Integration Tests**:

- [ ] T037 [US5] Test sort by created returns tasks in descending created_at order
- [ ] T038 [US5] Test sort by title returns tasks in alphabetical order
- [ ] T039 [US5] Test sort by priority returns tasks in order critical, high, medium, low
- [ ] T040 [US5] Test sort by updated returns tasks in descending updated_at order
- [ ] T041 [US5] Test default sort (no parameter) uses created descending

**Acceptance**: All sort options functional, default sort working

---

## Phase 8: US3 - Filter by Tag (P2)

**Story Goal**: Users can filter tasks by tag name

**Independent Test**: Filter by tag="work" returns only tasks with "work" tag

**Service Layer**:

- [ ] T042 [US3] Add tag filter logic with LEFT JOIN to get_user_tasks in backend/services/task_service.py (join TaskTag on Task.id == TaskTag.task_id, where TaskTag.tag_name == tag, add distinct())

**Integration Tests**:

- [ ] T043 [US3] Test filter by existing tag returns only tasks with that tag
- [ ] T044 [US3] Test filter by non-existent tag returns empty results
- [ ] T045 [US3] Test task with multiple tags appears when filtering by any tag
- [ ] T046 [US3] Test tag filter with tasks having no tags returns empty

**Acceptance**: Tag filtering functional with proper JOIN and DISTINCT

---

## Phase 9: US6 - Combine Multiple Filters (P3)

**Story Goal**: Users can apply multiple filters simultaneously

**Independent Test**: Combine search + priority + tag + status and get correct filtered results

**Integration Tests**:

- [ ] T047 [US6] Test combine search + priority filter (AND logic)
- [ ] T048 [US6] Test combine search + tag filter
- [ ] T049 [US6] Test combine priority + tag + status filters
- [ ] T050 [US6] Test combine all filters (search + priority + tag + status + sort)
- [ ] T051 [US6] Test combined filters with zero results returns empty array

**Acceptance**: Multiple filters combine correctly with AND logic

---

## Phase 10: Polish & Quality

**Goal**: Code quality, performance validation, documentation

**Performance**:

- [ ] T052 Test query performance with 1000 tasks (all filters <1.5s)
- [ ] T053 Test query performance with 10000 tasks (indexes used efficiently)
- [ ] T054 Verify EXPLAIN output shows index usage for priority and completed filters

**Code Quality**:

- [ ] T055 Run type checking with mypy (0 errors)
- [ ] T056 Verify code coverage ≥95% for modified files

**Documentation**:

- [ ] T057 Update OpenAPI documentation with new query parameters
- [ ] T058 Create IMPLEMENTATION_COMPLETE.md with summary

**Acceptance**: All quality gates passed

---

## Task Summary

**Total Tasks**: 58

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (US1 - Search): 6 tasks
- Phase 4 (US7 - Pagination): 10 tasks
- Phase 5 (US2 - Priority): 5 tasks
- Phase 6 (US4 - Status): 5 tasks
- Phase 7 (US5 - Sort): 8 tasks
- Phase 8 (US3 - Tag): 5 tasks
- Phase 9 (US6 - Combined): 5 tasks
- Phase 10 (Polish): 7 tasks

**By Type**:
- Setup/Verification: 7 tasks
- Implementation: 16 tasks
- Tests: 32 tasks
- Quality/Performance: 3 tasks

---

## Dependencies

**Story Completion Order**:
```
Phase 1 → Phase 2 →
US1 (Search) + US7 (Pagination) [Parallel or Sequential]
    ↓
US2 (Priority) || US4 (Status) [Parallel]
    ↓
US5 (Sort)
    ↓
US3 (Tag - requires JOIN)
    ↓
US6 (Combined)
    ↓
Polish
```

**Critical Path**: Phase 1 → Phase 2 → (US1 + US7) → (US2 || US4) → US5 → US3 → US6 → Polish

**Estimated Timeline**: ~5-6 hours

---

## Next Steps

Run `/sp.implement` with `query-optimization-specialist` agent to execute implementation.
