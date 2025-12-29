# Quickstart: Advanced Task Filtering and Search

**Feature**: Enhanced task list endpoint with filtering, search, sorting, pagination
**Status**: Planning Complete - Ready for Implementation

---

## Implementation Order

### 1. Update TaskListResponse Schema (15 min)
- Add `page: int` and `limit: int` fields
- File: `backend/schemas/task.py`

### 2. Enhance get_user_tasks Service (2 hours)
- Add query builder logic
- Implement search filter (ILIKE)
- Implement tag filter (JOIN)
- Implement sorting (CASE for priority)
- Separate count query
- File: `backend/services/task_service.py`

### 3. Update Route Handler (30 min)
- Add new query parameters (search, sort)
- Calculate page number from offset/limit
- File: `backend/routes/tasks.py`

### 4. Create Tests (2 hours)
- 32+ tests for all filter combinations
- File: `backend/tests/test_task_filtering.py`

**Total**: ~5 hours

---

## Key Design Patterns

1. **Query Builder**: Conditional filter application
2. **Index Optimization**: Use existing indexes for performance
3. **LEFT JOIN**: Tag filtering with DISTINCT
4. **Separate Count**: Total without loading all rows
5. **Limit Capping**: Enforce max 100 items per page

---

## Testing Focus

- Search with special characters (SQL injection prevention)
- Tag filtering with tasks having no tags
- Combined filters with zero results
- Pagination edge cases (offset > total)
- Performance with 10k+ tasks

---

## Success Criteria

- ✅ Search <2s, filters <1.5s (95th percentile)
- ✅ Handles 10k+ tasks
- ✅ All 32+ tests passing
- ✅ Code coverage ≥95%

---

## Agent & Skills

**Agent**: `query-optimization-specialist`
**Skills**: query-optimization, pagination-handling
