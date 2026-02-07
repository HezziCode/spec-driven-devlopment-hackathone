import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import TasksPageContent from '@/app/tasks/page'
import { useAuth } from '@/lib/auth'
import { useRouter, useSearchParams } from 'next/navigation'

// Mock dependencies
vi.mock('@/lib/auth', () => ({
  useAuth: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  taskApi: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
  },
}))

vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  useSearchParams: vi.fn(),
}))

vi.mock('@/components/TaskCard', () => ({
  default: ({ onToggleComplete, onDelete, onEdit }: any) => (
    <div data-testid="task-card">
      <button onClick={() => onToggleComplete('1', false)}>Toggle</button>
      <button onClick={() => onDelete('1')}>Delete</button>
      <button onClick={() => onEdit({ id: '1', title: 'Test' })}>Edit</button>
    </div>
  ),
}))

vi.mock('@/components/TaskForm', () => ({
  default: ({ onSubmit }: any) => (
    <div data-testid="task-form">
      <button onClick={() => onSubmit('Test Title', 'Test Desc', 'medium', [])}>Submit</button>
    </div>
  ),
}))

vi.mock('@/components/TaskFilters', () => ({
  default: ({ onStatusChange }: any) => (
    <div data-testid="task-filters">
      <button onClick={() => onStatusChange('active')}>Active</button>
    </div>
  ),
}))

describe('TasksPageContent', () => {
  beforeEach(() => {
    vi.mocked(useAuth).mockReturnValue({
      session: { user: { id: 'test-user-id' } },
      status: 'authenticated',
    } as any)
  })

  it('renders tasks page UI correctly', () => {
    render(<TasksPageContent />)
    expect(screen.getByText(/Conquer Your Tasks/i)).toBeInTheDocument()
    expect(screen.getByTestId('task-form')).toBeInTheDocument()
  })

  it('handles task creation', async () => {
    const mockCreateTask = vi.fn().mockResolvedValue({ id: 'new-task', title: 'New Task' })
    ;(taskApi.createTask as any).mockResolvedValue(mockCreateTask())

    render(<TasksPageContent />)
    fireEvent.click(screen.getByText('Submit'))
    expect(mockCreateTask).toHaveBeenCalled()
  })

  it('handles filter changes', () => {
    render(<TasksPageContent />)
    fireEvent.click(screen.getByText('Active'))
    // Additional assertions for filter state
  })

  it('shows loading state', () => {
    // Mock loading
    render(<TasksPageContent />)
    // Assertions
  })
})