export function getSelectedText(): string { return window.getSelection()?.toString().trim() ?? ''; }
