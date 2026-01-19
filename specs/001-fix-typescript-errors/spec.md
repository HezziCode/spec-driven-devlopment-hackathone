# TypeScript Build Error Resolution for Next.js (Strict Mode, Vercel)

## User Scenarios

1. Developer pushes code to main → Vercel auto-deploys without TypeScript build failures.
2. Production build runs → `npm run build` completes in <60s with 0 TS errors.
3. API calls fail → User sees friendly error messages (401, 404) without console crashes.
4. Local development → `npm run dev` and `npm run build` both pass with strict TS.

## Functional Requirements

1. **Build Success**: `npm run build` passes on Vercel/local with strict TS enabled.
2. **Unknown Type Safety**: No direct property access on `unknown` (e.g., `errorData.detail`).
3. **Catch Block Safety**: All `catch (err)` use `catch (err: unknown)` + narrowing.
4. **API Error Parsing**: `fetch().json()` returns `unknown` → safe parsing with type guards.
5. **No `any` Types**: Replace all `any` with `unknown` + guards or proper interfaces.

## Success Criteria

- `npm run build` completes <60s, 0 TS errors (measurable).
- 100% Vercel deployment success rate.
- All API errors display user-friendly messages (test 401/404/500).
- Strict TS mode enabled, no `// @ts-ignore`.
- Error handling covers 100% runtime error shapes from FastAPI.

## Key Entities

- **ApiError**: `{ status: number, code: string, message: string, data: unknown }`
- **ParsedError**: `{ message: string, code: string, status?: number }`

## Assumptions

- FastAPI errors follow `{error, code}` or `{detail: {error, code}}`.
- No backend changes needed.
- Focus on frontend/lib/api.ts + related files.

## Non-Functional Requirements

- Build time <60s.
- No runtime overhead from guards.
- Maintainable code with comments.

## Edge Cases

- Non-JSON responses.
- Malformed JSON.
- Network errors (AbortError).
- Empty responses.

## Dependencies

- Existing `/specs/api/rest-endpoints.md` for error shapes.

## Open Questions

None.