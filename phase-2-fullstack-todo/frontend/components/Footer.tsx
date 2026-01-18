'use client';

import Link from 'next/link';

interface FooterProps {
  variant?: 'default' | 'minimal';
}

/**
 * Footer Component
 *
 * Displays footer with links and copyright notice.
 * Supports two variants: default (full footer with all links) and minimal (compact for auth pages).
 *
 * @param variant - Footer style variant
 */
export default function Footer({ variant = 'default' }: FooterProps) {
  const currentYear = new Date().getFullYear();

  if (variant === 'minimal') {
    // Minimal footer for auth pages
    return (
      <footer className="w-full max-w-full py-6 px-4 border-t border-slate-700/50 bg-slate-900/30 overflow-x-hidden">
        <div className="max-w-md mx-auto w-full max-w-full">
          {/* Links */}
          <div className="flex justify-center items-center space-x-6 mb-3">
            <Link
              href="#terms"
              className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-200"
            >
              Terms of Service
            </Link>
            <span className="text-slate-600">•</span>
            <Link
              href="#privacy"
              className="text-sm text-slate-400 hover:text-cyan-400 transition-colors duration-200"
            >
              Privacy Policy
            </Link>
          </div>

          {/* Copyright */}
          <div className="text-center">
            <p className="text-xs text-slate-500">
              {currentYear} TaskFlow. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    );
  }

  // Default full footer
  return (
    <footer className="w-full max-w-full py-12 px-4 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-sm overflow-x-hidden">
      <div className="max-w-7xl mx-auto w-full max-w-full">
        {/* Footer Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-xl font-extrabold text-white">TaskFlow</span>
            </Link>
            <p className="text-sm text-slate-400">
              The modern way to manage your tasks.
            </p>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Social
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="https://www.linkedin.com/in/huzaifasys" target="_blank" rel="noopener noreferrer" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  LinkedIn
                </Link>
              </li>
              <li>
                <Link href="https://linktr.ee/huzaifasys" target="_blank" rel="noopener noreferrer" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Linktree
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Company
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/about" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Blog
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="#terms" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="#privacy" className="text-sm text-slate-400 hover:text-cyan-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Copyright */}
        <div className="pt-8 border-t border-slate-700/50">
          <p className="text-center text-sm text-slate-500">
            {currentYear} TaskFlow. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
