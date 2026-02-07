import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock next/navigation
vi.mock('next/navigation', async () => {
  const actual = await vi.importActual('next/navigation')
  return {
    ...actual,
    useRouter: vi.fn(),
    useSearchParams: vi.fn(),
    usePathname: vi.fn(),
  }
})

// Mock other Next.js modules as needed
