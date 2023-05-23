// 팝업 화면에서 이미지 출력하기
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.image) {
    const capturedImage = document.getElementById("capturedImage");
    capturedImage.src = message.image;
  }
});

// 액션 구현
document.addEventListener("DOMContentLoaded", () => {
  const captureButton = document.getElementById("captureButton");
  captureButton.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "openPopup" });
  });
});
