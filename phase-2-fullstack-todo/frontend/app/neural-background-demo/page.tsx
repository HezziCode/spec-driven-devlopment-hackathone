'use client';

import React from 'react';
import NeuralBackground from '@/components/NeuralBackground';

const NeuralBackgroundDemoPage = () => {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Neural Background Component */}
      <NeuralBackground
        particleCount={60}
        connectionDistance={100}
        particleColor="#22d3ee" // cyan-400 - optimized for dark theme
        connectionColor="#2dd4bf" // teal-400 - optimized for dark theme
      />

      {/* Content Overlay */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8 text-center">
        <div className="max-w-4xl mx-auto bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm p-12 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700">
          <h1 className="text-5xl font-bold text-slate-800 dark:text-white mb-6">
            Neural Particle Background
          </h1>

          <p className="text-xl text-slate-600 dark:text-slate-300 mb-8">
            Experience the dynamic neural network visualization with particles that move randomly and connect when close.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="bg-slate-100 dark:bg-slate-800 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Random Movement</h3>
              <p className="text-slate-600 dark:text-slate-400">Particles move with random velocities in the canvas space</p>
            </div>

            <div className="bg-slate-100 dark:bg-slate-800 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Dynamic Connections</h3>
              <p className="text-slate-600 dark:text-slate-400">Lines connect particles when they come within proximity</p>
            </div>

            <div className="bg-slate-100 dark:bg-slate-800 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Performance Optimized</h3>
              <p className="text-slate-600 dark:text-slate-400">Efficiently renders 60 particles with requestAnimationFrame</p>
            </div>
          </div>

          <div className="mt-12">
            <p className="text-slate-500 dark:text-slate-400 italic">
              The neural background runs efficiently in the background, creating a dynamic visualization that responds to window resizing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NeuralBackgroundDemoPage;