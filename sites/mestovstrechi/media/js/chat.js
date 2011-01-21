var chat_room_id = undefined;
var last_received = 0;
var chat_polling_time = 0;

function init_chat(chat_id, time) {
	chat_room_id = chat_id;
	chat_polling_time = time;
	sync_messages();
}

var img_dir = "/static/img/";

function get_comment_date(date){
	var date_str = String(date).split(".")[0];
	date_str = date_str.split(" ")[1];
	return date_str; 
}

function add_messages(messages){
	var templates = {
		'user': $.template("<p class='user'>(${date}) <b>${user}:</b> ${text}</p>"),
		'system': $.template("<p class='system'>(${date}) ${text}</p>")
	};
	
	for(var i in messages){
		var current = messages[i];

		$("#chat").append(templates[current.type] , {
		     date: get_comment_date(current.date),
		     user: current.user_name,
		     text: current.text
		});
	}
}

function set_last_message(json){
	if(json && json.length){
		last_received = json[json.length-1].date;
	}
}

/**
 * Asks the server which was the last message sent to the room, and stores it's id.
 * This is used so that when joining the user does not request the full list of
 * messages, just the ones sent after he logged in. 
 * @return
 */
function sync_messages() {
    $.ajax({
        type: 'POST',
        data: {
			id: window.chat_room_id
		},
        url:'/chat/sync/',
		dataType: 'json',
		success: function (json) {
			add_messages(json);
			set_last_message(json)
		}        
    });
	
	setTimeout("get_messages()", 2000);
}


/**
 * Gets the list of messages from the server and appends the messages to the chatbox
 */
function get_messages() {
    $.ajax({
        type: 'POST',
        data: {
			chat_id: window.chat_room_id, 
			offset: window.last_received
		},
        url:'/chat/receive/',
		dataType: 'json',
		success: function (json) {
            if (json) {
                add_messages(json);
                set_last_message(json);
                var $p_last = $('#chat p:last');
                if ($p_last && $p_last.offset() && $p_last.offset().top) {
                    $('.scroll-pane').scrollTop($p_last.offset().top);
                }
            }
			
		}        
    });
    
    // wait for next
    setTimeout("get_messages()", 2000);
}

/**
 * Tells the chat app that we are joining
 */
function chat_join() {
	$.ajax({
		async: false,
        type: 'POST',
        data: {
			chat_id: window.chat_room_id
		},
        url:'/chat/join/',
    });
}

/**
 * Tells the chat app that we are leaving
 */
function chat_leave() {
	$.ajax({
		async: false,
        type: 'POST',
        data: {
			chat_id: window.chat_room_id
		},
        url:'/chat/leave/',
    });
}

// attach join and leave events
$(window).load(function(){chat_join()});
$(window).unload(function(){chat_leave()});
