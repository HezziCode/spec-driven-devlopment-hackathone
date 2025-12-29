# CHUNK 6: Task Delete & Get Single - Implementation Complete ✅

**Feature**: Secure Task Deletion and Single Task Retrieval with GET by ID
**Date**: 2025-12-24
**Status**: ✅ **COMPLETE** - All tests passing, bugs fixed

---

## Summary

Successfully implemented secure task deletion (DELETE) and single task retrieval (GET by ID) endpoints with comprehensive security testing. Fixed critical tag serialization bugs and error handling issues to ensure proper API responses.

---

## Implemented Endpoints

### 1. GET /users/{user_id}/tasks/{task_id}
- **Purpose**: Retrieve a specific task by ID for authenticated user
- **Security**: User isolation, JWT verification, information disclosure prevention
- **Response**: Task details with tags serialized as string array
- **Status Codes**: 200 OK, 401 Unauthorized, 403 Forbidden, 404 Not Found

### 2. DELETE /users/{user_id}/tasks/{task_id}
- **Purpose**: Delete a specific task by ID for authenticated user
- **Security**: User isolation, JWT verification, cascade deletion of tags
- **Response**: Success message
- **Status Codes**: 200 OK, 401 Unauthorized, 403 Forbidden, 404 Not Found

---

## Implementation Details

### Service Layer (`backend/services/task_service.py`)

**`get_task_by_id(session, task_id, user_id)`**:
- Retrieves task by ID with user ownership verification
- Returns Task with TaskTag relationship intact (SQLModel handles loading)
- Returns None if task doesn't exist or belongs to different user

**`delete_task(session, task_id, user_id)`**:
- Verifies task ownership before deletion
- Manually deletes associated TaskTag records first (cascade)
- Deletes the task itself
- Returns boolean indicating success

**Key Fix**: Removed manual tag serialization in service layer - let SQLModel relationships work naturally.

### Route Layer (`backend/routes/tasks.py`)

**GET Endpoint** (`get_user_task`):
- Verifies user_id in path matches JWT token
- Retrieves task via service layer
- **Serializes TaskTag objects to strings** before response:
  ```python
  task_dict = task.model_dump()
  task_dict['tags'] = [tag.tag_name for tag in task.tags] if task.tags else []
  return TaskResponse(**task_dict)
  ```
- Proper exception handling (re-raises HTTPException)

**DELETE Endpoint** (`delete_user_task`):
- Verifies user_id in path matches JWT token
- Deletes task via service layer
- Returns 404 for non-existent tasks (security: prevents enumeration)
- **Proper exception handling** to avoid wrapping 404 in 500 error:
  ```python
  except HTTPException:
      raise  # Re-raise HTTPException as-is
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
  ```

---

## Bugs Fixed

### Bug 1: Tag Serialization in Service Layer ✅
**Problem**: Service functions were overwriting SQLModel relationships with string lists:
```python
# BEFORE (Bug):
task.tags = [tag.tag_name for tag in task.tags]  # Overwrites relationship
```

**Solution**: Removed manual serialization from service layer:
```python
# AFTER (Fixed):
return task  # SQLModel relationship intact
```

### Bug 2: Pydantic Validation Error ✅
**Problem**: TaskResponse expects `tags: List[str]` but Task.tags returns `List[TaskTag]`

**Solution**: Serialize in route handler before returning:
```python
task_dict = task.model_dump()
task_dict['tags'] = [tag.tag_name for tag in task.tags] if task.tags else []
return TaskResponse(**task_dict)
```

### Bug 3: DELETE Exception Handling ✅
**Problem**: Generic exception handler was catching HTTPException and wrapping 404 in 500 error

**Solution**: Re-raise HTTPException before generic handler:
```python
except HTTPException:
    raise  # Pass through HTTP exceptions
except Exception as e:
    raise HTTPException(status_code=500, ...)  # Only wrap unexpected errors
```

---

## Test Results

### GET Endpoint Tests (11/11 Passing) ✅
- ✅ `test_get_task_success_with_tags` - Task with tags returns properly serialized
- ✅ `test_get_task_with_no_tags` - Task without tags returns empty array
- ✅ `test_get_task_response_schema` - Response matches TaskResponse schema
- ✅ `test_get_task_non_existent_returns_404` - Non-existent task returns 404
- ✅ `test_get_task_cross_user_access_returns_404_not_403` - Security: returns 404 not 403
- ✅ `test_get_task_response_timing_consistent` - Timing attack prevention
- ✅ `test_get_task_path_user_mismatch_returns_403` - Path user mismatch returns 403
- ✅ `test_get_task_no_token_returns_401` - Missing token returns 401
- ✅ `test_get_task_invalid_token_returns_401` - Invalid token returns 401
- ✅ `test_get_task_expired_token_returns_401` - Expired token returns 401
- ✅ `test_get_task_invalid_uuid_format` - Invalid UUID format handled

### DELETE Endpoint Tests (13/13 Passing) ✅
- ✅ `test_delete_task_success_with_cascade` - Successful deletion with tag cascade
- ✅ `test_delete_task_no_tags` - Task without tags deletes cleanly
- ✅ `test_delete_task_cascade_multiple_tags` - Multiple tags cascade properly
- ✅ `test_delete_task_no_orphaned_tags` - No orphaned tags left in database
- ✅ `test_delete_task_non_existent_returns_404` - Non-existent task returns 404
- ✅ `test_delete_task_cross_user_access_returns_404_not_403` - Security: returns 404 not 403
- ✅ `test_delete_task_response_timing_consistent` - Timing attack prevention
- ✅ `test_delete_task_path_user_mismatch_returns_403` - Path user mismatch returns 403
- ✅ `test_delete_task_no_token_returns_401` - Missing token returns 401
- ✅ `test_delete_task_invalid_token_returns_401` - Invalid token returns 401
- ✅ `test_delete_task_idempotent` - DELETE is idempotent (second returns 404)
- ✅ `test_delete_task_invalid_uuid_format` - Invalid UUID format handled
- ✅ `test_delete_task_concurrent_attempts` - Concurrent deletions handled safely

### All Task Tests Combined (36/36 Passing) ✅
- GET security tests: 11 passing
- DELETE security tests: 13 passing
- CRUD tests: 12 passing (Create, List, Update, Patch)
- **Total: 36/36 tests passing**

---

## Security Features Implemented

1. **User Isolation**: All endpoints verify task ownership before operations
2. **Information Disclosure Prevention**: Returns 404 (not 403) for unauthorized access
3. **Timing Attack Prevention**: Consistent response times for existent vs non-existent tasks
4. **JWT Verification**: All endpoints require valid, non-expired JWT token
5. **Path Parameter Validation**: User ID in path must match JWT claim
6. **Cascade Deletion**: TaskTag records properly deleted with parent Task
7. **Idempotency**: DELETE can be called multiple times safely

---

## Files Modified

### Route Handler
- `backend/routes/tasks.py`:
  - Added tag serialization in GET/CREATE/PUT/PATCH endpoints
  - Fixed exception handling in DELETE endpoint

### Service Layer
- `backend/services/task_service.py`:
  - Removed incorrect tag serialization
  - Let SQLModel relationships work naturally

### Test Files
- `backend/tests/test_task_get_security.py` (11 tests)
- `backend/tests/test_task_delete_security.py` (13 tests)
- `backend/tests/test_tasks.py` (12 tests for CRUD)

---

## Compliance with REST API Specification

Fully compliant with `specs/api/rest-endpoints.md`:

- ✅ GET /users/{user_id}/tasks/{task_id} - Returns 200 with task details
- ✅ DELETE /users/{user_id}/tasks/{task_id} - Returns 200 with success message
- ✅ Authentication required for all endpoints
- ✅ User isolation enforced
- ✅ Proper status codes (200, 401, 403, 404)
- ✅ Tags serialized as string array in responses

---

## Next Steps

✅ **CHUNK 6 COMPLETE** - Ready to proceed with **CHUNK 7**

**Reminder**: Complete remaining backend chunks (7-12) before CHUNK 13 (Frontend-Backend Integration)

---

## Agent & Skills Used

- **Agent**: `security-focused-developer`
- **Skill**: `secure-resource-access`
- **Workflow**: /sp.specify → spec → plan → tasks → implement

---

## Notes

- Pydantic datetime.utcnow() deprecation warnings present but not blocking
- All security tests passing with proper timing attack prevention
- Tag serialization handled at route layer (not service layer)
- Exception handling properly re-raises HTTPException to avoid 500 wrapping
