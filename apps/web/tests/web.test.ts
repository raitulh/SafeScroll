import { describe, expect, it } from 'vitest';
import { API_BASE } from '../lib/api';
import { StaticPage } from '../components/StaticPage';

describe('Web App', () => {
  it('has a default API base URL', () => {
    expect(API_BASE).toBeDefined();
    expect(typeof API_BASE).toBe('string');
  });

  it('renders StaticPage with paragraphs', () => {
    const el = StaticPage({
      title: 'Test Title',
      eyebrow: 'TEST',
      paragraphs: ['Paragraph 1', 'Paragraph 2'],
    });
    expect(el).toBeDefined();
    expect(el.type).toBe('main');
  });
});
