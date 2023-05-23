document.addEventListener("DOMContentLoaded", function () {
  const captureButton = document.getElementById("captureButton");
  const imageContainer = document.getElementById("imageContainer");

  captureButton.addEventListener("click", function () {
    chrome.tabs.captureVisibleTab(function (screenshotUrl) {
      const image = new Image();
      image.src = screenshotUrl;
      imageContainer.innerHTML = "";
      imageContainer.appendChild(image);
    });
  });
});
