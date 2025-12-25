'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Waves } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* Wave-themed 404 icon */}
        <div className="mx-auto flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-r from-teal-100 to-cyan-100 dark:from-teal-900/30 dark:to-cyan-900/30 mb-6">
          <Waves className="w-12 h-12 text-teal-500 dark:text-teal-400" />
        </div>

        <h2 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
          Page Not Found
        </h2>

        <p className="text-slate-600 dark:text-slate-400 mb-8">
          Sorry, we couldn't find the page you're looking for. It may have been moved or doesn't exist.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-600 hover:to-cyan-600 text-white font-medium rounded-lg shadow-md transition-all duration-200 transform hover:scale-[1.02] active:scale-95"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}