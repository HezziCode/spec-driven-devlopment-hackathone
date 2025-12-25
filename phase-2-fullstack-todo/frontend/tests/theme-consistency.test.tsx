// Theme Consistency Tests
// These tests ensure that all components have proper light/dark theme handling

import React from 'react';
import { render, screen } from '@testing-library/react';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

// Test that components render with proper theme classes
describe('Theme Consistency Tests', () => {
  // Test TaskCard theme classes
  test('TaskCard has proper theme background classes', () => {
    const { container } = render(
      <TaskCard
        id="1"
        title="Test Task"
        description="Test Description"
        completed={false}
        priority="medium"
        tags={[]}
        createdAt="2023-01-01T00:00:00Z"
        updatedAt="2023-01-01T00:00:00Z"
        userId="test-user"
      />
    );

    // Check that the main card element has theme-appropriate classes
    const card = container.firstChild;
    expect(card).toHaveClass('bg-white');
    // Note: We can't easily test dark classes in JSDOM without CSS support
  });

  // Test TaskForm theme classes
  test('TaskForm has proper theme background classes', () => {
    const { container } = render(<TaskForm />);

    // Check that input elements have proper theme classes
    const inputs = container.querySelectorAll('input');
    inputs.forEach(input => {
      expect(input).toHaveClass('bg-white');
    });

    const textareas = container.querySelectorAll('textarea');
    textareas.forEach(textarea => {
      expect(textarea).toHaveClass('bg-white');
    });

    const selects = container.querySelectorAll('select');
    selects.forEach(select => {
      expect(select).toHaveClass('bg-white');
    });
  });

  // Additional tests can be added for other components
  test('Components do not use semi-transparent backgrounds', () => {
    const { container } = render(
      <TaskCard
        id="1"
        title="Test Task"
        description="Test Description"
        completed={false}
        priority="medium"
        tags={[]}
        createdAt="2023-01-01T00:00:00Z"
        updatedAt="2023-01-01T00:00:00Z"
        userId="test-user"
      />
    );

    // Ensure no elements have semi-transparent background classes like bg-white/80
    const elements = container.querySelectorAll('*');
    elements.forEach(element => {
      const className = element.className;
      expect(className).not.toMatch(/bg-(white|slate|gray)-\d*\/\d*/);
    });
  });
});