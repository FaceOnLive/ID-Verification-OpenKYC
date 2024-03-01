var result = JSON.parse($('#ocr-result').text() || '""')
    , $content = $('#result-content')
    , excludeFields = [
        'mrz_type',
        'valid_score',
        'type',
        'check_number',
        'check_date_of_birth',
        'check_expiration_date',
        'check_composite',
        'check_personal_number',
        'valid_number',
        'valid_date_of_birth',
        'valid_expiration_date',
        'valid_composite',
        'valid_personal_number',
    ];

$content.find('.row').remove();
var res_json = ''
if(('data' in result) && ('ocr' in result['data'])) {
    res_json = result['data']['ocr']
}
$.each(res_json, function(field, value) {
    if (excludeFields.indexOf(field) >= 0) return;
    var $row = $('<div></div>').addClass('row')
        , $col = $('<div></div>').addClass('col-lg-12')
        , $group = $('<div></div>').addClass('md-form')
        , $label = $('<label></label>').attr('for', 'id_' + field).addClass('active').text(field)
        , $input = $('<div/>').addClass('form-control').text(value);
    $group.append($label, $input);
    $col.append($group);
    $row.append($col);
    $content.append($row);
});