// 캡처 기능 구현
function captureVisibleTab() {
  chrome.tabs.captureVisibleTab(null, { format: "png" }, (imageDataUrl) => {
    chrome.runtime.sendMessage({ image: imageDataUrl });
  });
}

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

// "capture" 버튼 클릭 시 캡처 실행
document.addEventListener("DOMContentLoaded", () => {
  const captureButton = document.getElementById("captureButton");
  captureButton.addEventListener("click", captureVisibleTab);
});
