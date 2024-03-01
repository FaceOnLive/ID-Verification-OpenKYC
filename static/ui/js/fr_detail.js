window.addEventListener("flutterInAppWebViewPlatformReady", null); // add event to send message to app


$('#btn-done').click(function() {
    var ocrResult = JSON.parse($('#ocr-result').text() || '""')
        , frResult = JSON.parse($('#fr-result').text() || '""')
        , url = JSON.parse($('#ocr-type-url').text() || '""');

    try { window.flutter_inappwebview.callHandler('ocrResult', ocrResult); } catch(error) {}
    try { window.flutter_inappwebview.callHandler('frResult', frResult); } catch(error) {}
    try { window.flutter_inappwebview.callHandler('isDone', true); } catch(error) {}
    window.location.href = url;
});
