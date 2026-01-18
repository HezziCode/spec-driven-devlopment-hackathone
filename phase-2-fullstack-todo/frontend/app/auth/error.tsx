'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Authentication error:', error);
  }, [error]);

  return (
    <div className="error-container">
      <h2>The requested resource was not found</h2>
      <p>We couldn't find the page you're looking for.</p>
      <div className="error-actions">
        <button
          onClick={
            () => {
              reset();
              router.push('/'); // Redirect to home
            }
          }
          className="btn-secondary"
        >
          Go to Home
        </button>
        <button
          onClick={() => router.back()}
          className="btn-outline"
        >
          Go Back
        </button>
      </div>
    </div>
  );
}