var msg_container;
var err_container;
var suc_container;
var interval_ref = null;
var progress_ref = null;
$(document).ready(function(){
	if (json_url != ''){
		$('#progress-bar-container').show();
		msg_container = $('.process-messages');
		err_container = $('.alert-danger');
		suc_container = $('.alert-success');
		link = $('#download-link');
		process_json();
		interval_ref = setInterval(process_json, 400);
		progress_ref = setInterval(progress, 60);
	}
});


function process_json(){
	if(interval_ref != null){
		$.getJSON(json_url, function( data ) {
		console.log(data);
		msg_container.show();
		msg_container.html(str2html(data.log));
		
		done = (new Date() - start)/expected_ms * 100;
		$('.progress-bar').css('width', done+'%');
		if (data.complete){
			clearInterval(interval_ref);
			if (data.successful){
				suc_container.show();
				if (act == 'IM'){
					suc_container.text('Data successfully imported.');
				} else {
					suc_container.text('Data successfully exported, click below to download.');
					link.show();
					link.attr('href', media_url+data.imex_file);
				}
			} else {
				err_container.show();
				err_container.html(str2html(data.errors));
			}
			clearInterval(progress_ref);
			$('.progress').removeClass('active');
			$('.progress-bar').css('width', '100%');
		}
		});
	}
}

function str2html(str){
	var re = new RegExp('\n', 'g');
	return '<p>' + str.replace(re,'</p>\n<p>') + '</p>';
}

var start = new Date();
function progress(){
	done = (new Date() - start)/expected_ms * 100;
	$('.progress-bar').css('width', done+'%');
	if (done>100)
		clearInterval(progress_ref);
}