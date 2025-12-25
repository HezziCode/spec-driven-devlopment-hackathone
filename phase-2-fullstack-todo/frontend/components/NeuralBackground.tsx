'use client';

import React, { useEffect, useRef } from 'react';

/**
 * Represents a particle in the neural background system
 */
interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

/**
 * Properties for the NeuralBackground component
 */
interface NeuralBackgroundProps {
  /**
   * Number of particles to render (default: 60)
   * @default 60
   */
  particleCount?: number;

  /**
   * Maximum distance for particles to connect with lines (default: 100)
   * @default 100
   */
  connectionDistance?: number;

  /**
   * Color for the particles (default: '#22d3ee' - cyan-400, optimized for dark theme)
   * @default '#22d3ee'
   */
  particleColor?: string;

  /**
   * Color for the connections between particles (default: '#2dd4bf' - teal-400, optimized for dark theme)
   * @default '#2dd4bf'
   */
  connectionColor?: string;

  /**
   * Additional CSS classes to apply to the container
   * @default ''
   */
  className?: string;
}

/**
 * NeuralBackground Component
 *
 * A dynamic canvas-based background with particles that move randomly and connect
 * with lines when they come close to each other. The background is fixed behind
 * all content and automatically resizes with the window.
 *
 * Features:
 * - Smooth particle movement with boundary collision
 * - Distance-based connections between particles
 * - Optimized performance using requestAnimationFrame
 * - Responsive design that adapts to window resizing
 * - Proper cleanup to prevent memory leaks
 *
 * @param {NeuralBackgroundProps} props - Configuration options for the neural background
 * @returns {JSX.Element} The neural background component
 */
const NeuralBackground: React.FC<NeuralBackgroundProps> = ({
  particleCount = 60,
  connectionDistance = 100,
  particleColor = '#22d3ee', // cyan-400 - brighter for dark theme
  connectionColor = '#2dd4bf', // teal-400 - brighter for dark theme
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Initialize particles with random positions and velocities
   * @returns {Particle[]} Array of initialized particles
   */
  const initParticles = (): Particle[] => {
    if (!containerRef.current) return [];

    const { width, height } = containerRef.current.getBoundingClientRect();
    const particles: Particle[] = [];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5, // Reduced velocity for smoother movement
        vy: (Math.random() - 0.5) * 0.5,
        radius: 2 // Increased radius for better visibility in dark theme
      });
    }

    return particles;
  };

  /**
   * Update particle positions and handle boundary collisions
   */
  const updateParticles = (): void => {
    if (!containerRef.current) return;

    const { width, height } = containerRef.current.getBoundingClientRect();

    particlesRef.current.forEach(particle => {
      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;

      // Boundary collision - bounce off edges
      if (particle.x <= 0 || particle.x >= width) {
        particle.vx *= -1;
      }
      if (particle.y <= 0 || particle.y >= height) {
        particle.vy *= -1;
      }

      // Keep particles within bounds
      particle.x = Math.max(0, Math.min(width, particle.x));
      particle.y = Math.max(0, Math.min(height, particle.y));
    });
  };

  /**
   * Draw particles and connections on the canvas
   */
  const draw = (): void => {
    const canvas = canvasRef.current;
    if (!canvas || !containerRef.current) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = containerRef.current.getBoundingClientRect();

    // Set canvas size to match container
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw connections between nearby particles
    // Optimized: Calculate squared distance to avoid expensive sqrt operation
    const particles = particlesRef.current;
    const len = particles.length;
    const maxDistanceSquared = connectionDistance * connectionDistance;

    for (let i = 0; i < len; i++) {
      const p1 = particles[i];

      for (let j = i + 1; j < len; j++) {
        const p2 = particles[j];

        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distanceSquared = dx * dx + dy * dy;

        if (distanceSquared < maxDistanceSquared) {
          // Calculate actual distance only when needed for opacity
          const distance = Math.sqrt(distanceSquared);
          const opacity = 1 - distance / connectionDistance;

          ctx.beginPath();
          ctx.strokeStyle = `${connectionColor}${Math.floor(opacity * 200).toString(16).padStart(2, '0')}`;
          ctx.lineWidth = 1; // Increased line width for better visibility in dark theme
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
    }

    // Draw particles
    for (let i = 0; i < len; i++) {
      const particle = particles[i];
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      ctx.fillStyle = particleColor;
      ctx.fill();
    }
  };

  /**
   * Animation loop using requestAnimationFrame
   */
  const animate = (): void => {
    updateParticles();
    draw();
    animationFrameRef.current = requestAnimationFrame(animate);
  };

  /**
   * Handle window resize events
   */
  const handleResize = (): void => {
    if (containerRef.current) {
      // Clear existing particles to avoid accumulation
      particlesRef.current = initParticles();
    }
  };

  // Setup and cleanup
  useEffect(() => {
    if (containerRef.current) {
      particlesRef.current = initParticles();
      animate();

      window.addEventListener('resize', handleResize);

      return () => {
        cancelAnimationFrame(animationFrameRef.current);
        window.removeEventListener('resize', handleResize);
      };
    }
  }, []);

  return (
    <div
      ref={containerRef}
      className={`fixed inset-0 -z-10 overflow-hidden ${className}`}
      style={{ background: 'transparent' }} // Ensure transparent background
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ display: 'block' }} // Ensure canvas is visible
      />
    </div>
  );
};

export default NeuralBackground;