chrome.action.onClicked.addListener(function (tab) {
  chrome.tabs.captureVisibleTab(function (screenshotUrl) {
    // 캡처된 이미지를 사용하여 원하는 작업 수행
    // 예: 이미지 저장, API 전송 등
    console.log(screenshotUrl);
  });
});
