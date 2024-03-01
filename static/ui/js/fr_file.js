// do not compress more than declared below, otherwise canvas will be blank
// https://github.com/jhildenbiddle/canvas-size
var maxCanvasWidth = 4096, maxCanvasHeight = 4096;
// accepted file type on uploading
var acceptedFileType = ['jpg', 'jpeg', 'png'];
// compressor options, for compressing captured and uploaded image
Compressor.setDefaults({
    mimeType: 'image/png',
    maxWidth: 1050,
    maxHeight: 800,
    convertSize: 2000000,
});


// file change
$('.file-capture').change(function() {
    var file = event.target.files[0]
        , $img = $('#img-preview');

    if (file === undefined) modalAlert(gettext('Invalid Image'), gettext('No image file selected'));
    new Compressor(file, {
        success: function(result) {
            blobToDataURL(result, function(dataURL) {
                $img.attr('src', dataURL);
                $('.page-header, .page-subheader, .default-container, .webcam-container').hide();
                $('.preview-container, #btn-skip').show();
            });
        },
        error: function(err) {
            console.error('Compressor() error:'+ err.message);
            modalAlert(gettext('Error'), gettext('Error capturing image'));
        },
    });
});


// btn-next click
$('#btn-next').click(function() {
    var imgData = $('#img-preview').attr('src')
        , imgType = imgData.substring("data:image/".length, imgData.indexOf(";base64"))
        , index = imgType == 'jpeg' ? 23 : 22
        , $frFile = $('#id_fr_file');
    
    $frFile.val(imgData.substring(index)); // remove `data:image/png;base64,` or `data:image/jpeg;base64,` on dataURL
    $('#form-fr').submit();
});


// blob to dataURL
function blobToDataURL(blob, callback) {
    var reader = new FileReader();
    reader.onload = function(e) { callback(e.target.result); }
    reader.readAsDataURL(blob);
}


// dataURL to blob
function dataURLtoBlob(dataURL) {
    var arr = dataURL.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type:mime});
}
