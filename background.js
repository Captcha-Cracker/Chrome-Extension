// 팝업 열기 및 버튼 클릭 이벤트 처리
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "openPopup") {
    chrome.windows.create({
      url: chrome.runtime.getURL("popup.html"),
      type: "popup",
      width: 400,
      height: 400,
    });
  }
});

// 클릭 이벤트 핸들러
chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.insertCSS({
    target: { tabId: tab.id },
    files: ["styles.css"],
  });

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["capture.js"],
  });

  chrome.runtime.sendMessage({ action: "openPopup" });
});
