document.addEventListener("DOMContentLoaded", async function () {
  const captureButton = document.getElementById("captureButton");
  const imageContainer = document.getElementById("imageContainer");
  const resultButton = document.getElementById("resultButton");
  let isCapturing = false;
  let startX, startY;

  captureButton.addEventListener("click", function () {
    if (!isCapturing) {
      isCapturing = true;
      captureButton.textContent = "Stop Capture";
      document.body.style.cursor = "crosshair";
    } else {
      isCapturing = false;
      captureButton.textContent = "Capture";
      document.body.style.cursor = "default";
    }
  });

  document.addEventListener("mousedown", function (event) {
    if (isCapturing) {
      startX = event.clientX;
      startY = event.clientY;
    }
  });

  document.addEventListener("mouseup", function (event) {
    if (isCapturing) {
      const endX = event.clientX;
      const endY = event.clientY;

      const left = Math.min(startX, endX);
      const top = Math.min(startY, endY);
      const width = Math.abs(endX - startX);
      const height = Math.abs(endY - startY);

      chrome.tabs.captureVisibleTab(function (screenshotUrl) {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        const image = new Image();
        image.onload = function () {
          canvas.width = width;
          canvas.height = height;
          context.drawImage(image, left, top, width, height, 0, 0, width, height);

          const capturedImageUrl = canvas.toDataURL("image/png");
          const capturedImage = new Image();
          capturedImage.src = capturedImageUrl;

          imageContainer.innerHTML = "";
          imageContainer.appendChild(capturedImage);

          // 이미지 다운로드 링크 생성
          const link = document.createElement("a");
          link.href = capturedImageUrl;
          link.download = "captured_image.png";
          link.click(); // 자동으로 다운로드됨

          resultButton.addEventListener("click", function () {
            document.write(`<h1>hello</h1>`);
            // var pythonScript = document.createElement("script");
            // pythonScript.src = "/Chrome-Extension/hello.py";
            // document.body.appendChild(pythonScript);
          });
        };

        image.src = screenshotUrl;
      });

      isCapturing = false;
      captureButton.textContent = "Capture";
      document.body.style.cursor = "default";
    }
  });
});
