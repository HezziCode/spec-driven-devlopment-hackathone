# Quickstart: TaskWave Dashboard

## Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.11+ with uv package manager
- Next.js 16+ project with App Router
- Better Auth configured for authentication
- Backend API with task endpoints

## Setup Steps

### 1. Environment Configuration
```bash
# Ensure you have the required environment variables set:
# - BETTER_AUTH_SECRET (for JWT verification)
# - NEXT_PUBLIC_API_BASE_URL (for API calls)
```

### 2. Install Dependencies
```bash
# In frontend directory
cd frontend
npm install  # or pnpm install
```

### 3. Create the Dashboard Route
Create the file `frontend/app/tasks/page.tsx` with the protected dashboard implementation.

### 4. Implement Components
- Create `TaskCard.tsx` for interactive task cards
- Create `TaskForm.tsx` for task creation
- Create `TaskFilters.tsx` for filtering/sorting/searching
- Create `ProFeatureTeaser.tsx` for premium features
- Create `StreakCounter.tsx` for gamification

### 5. API Integration
- Use the existing API client from `frontend/lib/api.ts`
- Ensure JWT tokens are attached to requests
- Handle loading and error states appropriately

### 6. Styling
- Apply wave-themed animations using Tailwind CSS
- Implement hover effects (scale-110/translate-y-1)
- Use teal-cyan gradient theme consistently
- Ensure light/dark mode compatibility

## Running the Dashboard

```bash
# Start the Next.js development server
cd frontend
npm run dev  # or pnpm dev

# The dashboard will be available at:
# http://localhost:3000/tasks
```

## Testing the Dashboard

1. Ensure you're logged in (auth should redirect if not)
2. Verify task cards display with wave-themed styling
3. Test creating new tasks with the form
4. Verify filtering, searching, and sorting functionality
5. Check streak counter updates properly
6. Confirm pro feature teaser displays correctly

## Key Features to Verify

- **Authentication Protection**: Unauthenticated users redirected to /auth
- **Interactive Task Cards**: Hover animations and priority badges
- **Task Creation Form**: With tag chips and priority selection
- **Filtering/Searching**: By status, priority, and search terms
- **Gamification**: Streak counter updates on task completion
- **Pro Features**: Blurred teaser section with upgrade button
- **Accessibility**: Keyboard navigation and screen reader support
- **Responsive Design**: Works on mobile, tablet, and desktop

## Troubleshooting

- If authentication fails, check that JWT tokens are properly configured
- If API calls fail, verify backend endpoints are running and accessible
- If styling doesn't appear, ensure Tailwind CSS is properly configured
- If animations don't work, check that Tailwind's animation utilities are enabled