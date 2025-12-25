name: implement_tasks_page
title: Implement Tasks Page (frontend-only) — "Tasks Page: Phase II"
description: |
  Implement a focused, elegant Tasks page UI for the Phase II Todo Full-Stack app.
  This skill updates the Next.js frontend only (frontend/...). Do NOT modify backend files.
  Key goals: simplify the Tasks page, match the homepage theme (curved heading line), move "Add new task"
  to the top, make the primary CTA small and styled, remove cluttered boxes/stats, use a single background,
  implement optimistic UI removal on task completion (frontend-only mock), rename public app label away from
  "TaskWave" (provide suggested name), and keep the page responsive and accessible.

  This skill must follow the frontend CLAUDE.md patterns:
  - Next.js App Router (server components by default; use client components only for interactive parts)
  - TypeScript
  - Tailwind CSS
  - Use /lib/api.ts for real API calls; for now implement a lightweight mock client and toggle to real client via config flag.

tags:
  - frontend
  - nextjs
  - typescript
  - tailwind
  - ui
  - tasks

inputs:
  newAppName:
    type: string
    required: false
    default: "Taskory"
    description: "New public name for the app (replace TaskWave). Default provided if omitted."
  primaryColor:
    type: string
    required: false
    default: "bg-sky-600"
    description: "Tailwind class (or hex) for primary UI color used in headings/buttons."
  ctaButtonColor:
    type: string
    required: false
    default: "bg-emerald-500"
    description: "Tailwind class (or hex) for the small add-task button."
  useMockApi:
    type: boolean
    required: false
    default: true
    description: "If true, implement mock frontend-only API (local state). If false, hook into /lib/api.ts."
  filesToEdit:
    type: array
    required: false
    default:
      - "frontend/app/tasks/page.tsx"
      - "frontend/components/tasks/AddTaskForm.tsx"
      - "frontend/components/tasks/TaskList.tsx"
      - "frontend/components/ui/CurvedHeading.tsx"
      - "frontend/lib/mockApi.ts"
      - "frontend/lib/api.ts (conditional)"
      - "frontend/types/index.ts"
      - "frontend/styles/globals.css"
    description: "Paths to edit/create. Adjust to repo layout if different."

outputs:
  changed_files:
    type: array
    description: "List of files created or modified by the implementation."
  acceptance:
    type: object
    description: |
      Acceptance checks and their pass/fail. Should include:
       - addTaskOnTop: boolean
       - ctaSmallAndStyled: boolean
       - curvedHeadingPresent: boolean
       - clutterRemoved: boolean
       - completeRemovesTaskInUI: boolean
       - mockApiToggle: boolean

run:
  - step: "Read context"
    instructions: |
      Read frontend/CLAUDE.md, frontend/types/index.ts, and frontend app layout to match design conventions.
      Do NOT modify backend/. Only touch files listed in inputs.filesToEdit (or their equivalents).

  - step: "Rename public app label"
    instructions: |
      Replace occurrences of the public app name "TaskWave" displayed on UI pages (header, meta titles for Tasks page)
      with the provided input.newAppName (default Taskory). Do NOT change internal repo names or backend identifiers.
      Update /app/layout.tsx or header component where the public brand text is rendered.

  - step: "Simplify Tasks page (structure & content)"
    instructions: |
      Implement a clean, mobile-first Tasks page that:
      - Removes the following UI elements entirely from the tasks page: "Wave Streak: 5 days", "Your longest streak: 12 days", "Last completed", "5 days ago", "🔥 You're on fire! Keep going!" and any additional large hero boxes that make the page feel overloaded.
      - Keep the overall theme (colors, fonts) consistent with the Home page.
      - Use a single background on the page (e.g., a soft gradient or single background image class) — do NOT create multiple background layers.
      - Make the hero section subtle: no big cards, instead show the curved heading (see next step) and a short one-line subtitle.
      - Place the "Add New Task" form at the very top of the content area (below header & heading).
      - Display the task list under the add form. Each task row shows title, optional short description truncated to 120 chars, due date (if present), and an action button to 'Complete' (or ✓).
      - When 'Complete' is clicked, remove the task from the UI (optimistic update). Do not call backend if useMockApi=true; if useMockApi=false, call api.deleteTask or api.completeTask and still remove optimistically.

  - step: "Curved heading component"
    instructions: |
      Create `frontend/components/ui/CurvedHeading.tsx` (client or server as appropriate).
      The component renders:
        - an H1 with the app section name (e.g., "{newAppName} — Tasks")
        - a thin SVG curve that starts at left and arcs under the H1 similar to homepage curve style — keep it minimal and accessible.
      Example (TypeScript + Tailwind):
      ```tsx
      // frontend/components/ui/CurvedHeading.tsx
      import React from "react";

      export default function CurvedHeading({title, subtitle}:{title:string; subtitle?:string}) {
        return (
          <div className="mb-6">
            <h1 className="text-3xl font-extrabold tracking-tight">
              {title}
            </h1>
            <div aria-hidden className="mt-1">
              <svg viewBox="0 0 600 20" className="w-full h-6">
                <path d="M0 10 C150 0 450 20 600 10" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            {subtitle && <p className="text-sm opacity-80 mt-2">{subtitle}</p>}
          </div>
        );
      }
      ```
      Use the primaryColor input to style the SVG stroke and H1 (convert Tailwind class to className or inline style if a hex is provided).

  - step: "AddTaskForm component (client component)"
    instructions: |
      Create or update `frontend/components/tasks/AddTaskForm.tsx` as a client component.
      Requirements:
        - Minimal, compact layout: small input for title and optional description textarea.
        - The primary action button must be visually small (use `px-3 py-1.5 text-sm rounded`) and use input.ctaButtonColor.
        - Button label: "Add task" (not "Deploy strategy" — replace that text).
        - On submit, call the frontend API client:
           - if useMockApi=true -> use frontend/lib/mockApi.createTask(...)
           - else -> use lib/api.ts -> api.createTask(userId, payload)
        - After success, clear form and add the newly created task to the top of the task list (optimistic append).
        - Validate title: required, 1–200 chars. Show inline error text (small, red) under the field.
      Example form handlers should be included in the file.

  - step: "TaskList & TaskItem components"
    instructions: |
      Create `frontend/components/tasks/TaskList.tsx` and optionally `TaskItem.tsx`.
      Requirements:
        - Accept initialTasks prop (Task[]).
        - Render tasks in a vertical list with compact rows.
        - Each row has:
            - Title (bold)
            - Short description (muted)
            - Due date (muted, small)
            - Small 'Complete' button (text or icon) on the right.
        - When 'Complete' is clicked:
            - Immediately remove the item from local UI state (optimistic removal).
            - If useMockApi=false, trigger backend PATCH /api/{user_id}/tasks/{id}/complete and handle errors by restoring the item if the call fails.
        - Provide aria attributes for the buttons and roles for list semantics.

  - step: "Mock API client"
    instructions: |
      If useMockApi=true: create `frontend/lib/mockApi.ts` providing:
        - getTasks(userId): Promise<Task[]>
        - createTask(userId, payload): Promise<Task>
        - completeTask(userId, taskId): Promise<void>
        - deleteTask(userId, taskId): Promise<void>
      Implementation may use localStorage to persist across reloads for dev convenience. Keep interfaces identical to real api.ts to make swapping easy.

  - step: "API integration note"
    instructions: |
      If useMockApi=false: ensure the UI uses `frontend/lib/api.ts` functions:
        - api.getTasks(userId)
        - api.createTask(userId, payload)
        - api.completeTask(userId, taskId)
      If `frontend/lib/api.ts` is missing, add small wrapper stubs that call fetch('/api/...') so that the page remains functional and easy to replace later.

  - step: "Types update"
    instructions: |
      Update `frontend/types/index.ts` (or ensure Task types exist) with:
      ```ts
      export interface Task {
        id: number;
        user_id: string;
        title: string;
        description?: string;
        completed: boolean;
        due_date?: string;
        created_at: string;
        updated_at: string;
      }

      export interface TaskFormData {
        title: string;
        description?: string;
        dueDate?: string;
      }
      ```
      Keep backend naming (snake_case) for API responses; for form state you may use camelCase.

  - step: "Styling changes"
    instructions: |
      - Use Tailwind utility classes, follow frontend style tokens.
      - Make CTA (Add task) small: `px-3 py-1.5 text-sm rounded-md` and use input.ctaButtonColor for background and `text-white` for contrast unless color is hex (then inline style).
      - Ensure headings and curve use the input.primaryColor.
      - Remove large hero card — replace with the CurvedHeading component and a one-line subtitle.
      - Single page background: choose `bg-gradient-to-b from-slate-50 to-white` or a single image class; do not add multiple boxes.

  - step: "Accessibility & responsiveness"
    instructions: |
      - Ensure all interactive elements (buttons, inputs) have accessible labels and focus states.
      - Ensure layout stacks vertically on small screens with reasonable spacing.
      - Tasks list should be keyboard navigable.

  - step: "Behavior acceptance tests (manual check list to include in output)"
    instructions: |
      After implementation, perform these checks and return acceptance booleans in outputs.acceptance:
        1. New public app name shows on header and Tasks page title.
        2. Curved heading displays under the H1 and uses primary color.
        3. Add Task form is at the top and the add button is small and styled with CTA color.
        4. Hero boxes/stats (streaks, last completed, big hero) are removed from Tasks page.
        5. Clicking Add immediately inserts the task at the top of the list.
        6. Clicking Complete removes the task from the UI immediately.
        7. All changes are responsive and accessible.

  - step: "Files & patches"
    instructions: |
      For each file edited or created, follow the repo's existing patch format (e.g., create patch diff or edit in-place). Include concise commit message per file: e.g., "feat(tasks): implement elegant tasks page + mock API + curved heading".
      Provide a final list of changed files and short rationale for each change in outputs.changed_files.

  - step: "If you encounter ambiguity"
    instructions: |
      Make a best-effort decision without pausing:
        - Choose the default newAppName "Taskory" if user doesn't provide one.
        - Choose useMockApi=true by default.
        - Keep UI sizes compact and conservative.
      Do NOT ask for confirmation; implement using the defaults.

examples:
  - title: "Default run"
    input:
      newAppName: "Taskory"
      primaryColor: "bg-sky-600"
      ctaButtonColor: "bg-emerald-500"
      useMockApi: true
    expected_result_summary: |
      - frontend/components/ui/CurvedHeading.tsx created
      - frontend/components/tasks/AddTaskForm.tsx created (client)
      - frontend/components/tasks/TaskList.tsx created
      - frontend/lib/mockApi.ts created using localStorage
      - frontend/app/tasks/page.tsx replaced with new elegant layout (AddTask on top)
      - Header/app name replaced with "Taskory"
      - Acceptance checks all true

notes: |
  - This skill modifies ONLY the frontend. Backend work will be implemented later; ensure API hooks are present and consistent with /specs/api/rest-endpoints.md.
  - Keep changes conservative: remove only the specified heavy UI elements; preserve homepage theme and global header/footer.
  - Follow TypeScript strict mode where possible. Use `use client` directive only for interactive components.
  - Prefer server components for the page shell and initial data fetching (if not using mock api); keep client components for form and list interactivity.

