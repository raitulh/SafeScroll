chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: 'safescroll-scan-selection', title: 'Scan selected text with SafeScroll', contexts: ['selection'] });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== 'safescroll-scan-selection' || !tab?.id) return;
  const selected = info.selectionText ?? '';
  await chrome.storage.session.set({ safescrollLastSelection: selected });
  try { await chrome.action.openPopup(); } catch { /* popup can be opened manually */ }
});
