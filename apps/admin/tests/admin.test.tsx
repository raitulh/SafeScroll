import { describe, expect, it } from 'vitest';
import AdminPage from '../app/page';

describe('AdminPage', () => {
  it('renders admin control center structure', () => {
    const el = AdminPage();
    expect(el).toBeDefined();
    expect(el.type).toBe('main');
  });
});
