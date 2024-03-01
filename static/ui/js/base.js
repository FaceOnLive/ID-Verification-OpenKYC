// add loading when page is loading
$('body').addClass('loading');
$(window).on('load', function() {
	// remove loading when page is loaded
    $('body').removeClass('loading');

	// alert using modal when loading is removed
	$('.modal.auto-show').each(function() {
		if (!$('body').hasClass('modal-open')) {
			$(this).modal('show').addClass('shown');
		}
		// trigger next modal
		$(this).on('hidden.bs.modal', function(e) {
			$('.modal.auto-show:not(.shown)').first().modal('show').addClass('shown');
		});
	});
});
// add loading when form submit
$('form').submit(function() {
    if (!$('body').hasClass('live')) $('body').addClass('loading');
});
// add loading when ajax
$(document).on({
    ajaxStart: function() { if (!$('body').hasClass('live')) $('body').addClass('loading'); },
    ajaxStop: function() { $('body').removeClass('loading'); }
});


// notification using bootstrap toast
//$('.toast').toast('show');


// initiate and show alert modal
function modalAlert(title=gettext('Error'), body=gettext('Error'), btnDismissText=gettext('Close')) {
    var modal =
        '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true">' +
            '<div class="modal-dialog modal-dialog-centered modal-sm">'+
                '<div class="modal-content">'+
                    '<div class="modal-header">'+
                        '<div class="modal-title mx-auto" id="modal-label-{{ forloop.counter0 }}">'+ title +'</div>'+
                    '</div>'+
                    '<div class="modal-body">'+ body +'</div>'+
                    '<div class="modal-footer">'+
                        '<button type="button" class="btn btn-primary mx-auto" data-dismiss="modal">'+ btnDismissText +'</button>'+
                    '</div>'+
                '</div>'+
            '</div>'+
        '</div>';

    $('.wrapper').append(modal);
    $('.modal:last').modal('show').addClass('shown');
}
