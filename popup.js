function executeScript(e) {
  chrome.tabs.executeScript(null, {
    code: "document.querySelector('.captcha-input').value='123';"
  });
}

document.addEventListener("DOMContentLoaded", function() {
  var btn01 = document.querySelector('#btn');
  btn01.addEventListener("click", executeScript);
});
