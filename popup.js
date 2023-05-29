import * as tf from "tensorflow.js";

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

          resultButton.addEventListener("click", function () {
            // 이미지를 모델에 전달하고 결과를 팝업 창에 출력하는 부분입니다.
            // const tensor = tf.browser.fromPixels(capturedImage).expandDims();
            // const prediction = model.predict(tensor);
            // const result = prediction.dataSync();
            // document.write(`<h1>Prediction Result: ${result}</h1>`);
            document.write(`<h1>hello</h1>`);
          });
        };
        image.src = screenshotUrl;
      });

      isCapturing = false;
      captureButton.textContent = "Capture";
      document.body.style.cursor = "default";
    }
  });

  const modelPath = "captcha_recognition_model.h5";
  const model = await tf.loadLayersModel(modelPath);
});
