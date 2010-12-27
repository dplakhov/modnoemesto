var chat_room_id = undefined;
var last_received = 0;
var chat_polling_time = 0;

/**
 * Initialize chat:
 * - Set the room id
 * - Generate the html elements (chat box, forms & inputs, etc)
 * - Sync with server
 * @param chat_room_id the id of the chatroom
 * @param html_el_id the id of the html element where the chat html should be placed
 * @return
 */
function init_chat(chat_id, time) {
	chat_room_id = chat_id;
	chat_polling_time = time;
	sync_messages();
}

var img_dir = "/static/img/";

function add_messages(messages){
	var html_messages = [];
	for(var i in messages){
		var current = messages[i];
		var html_message = "<p>"+
		"("+String(current.date).split(".")[0]+") <b>"+current.user_name+":</b> "+current.text+"</p>";
		html_messages.push(html_message);
	}
	$("#chat").append(html_messages.join(""));
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
			var scroll = false;
		
			// first check if we are at the bottom of the div, if we are, we shall scroll once the content is added
			var $containter = $("#chat");
			if ($containter.scrollTop() == $containter.attr("scrollHeight") - $containter.height())
				scroll = true;

			// add messages
			add_messages(json);
			set_last_message(json)
			
			
			// scroll to bottom
			if (scroll)
				$("#chat").animate({ 
					scrollTop: $("#chat").attr("scrollHeight") 
					}, 500);
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
			chat_room_id: window.chat_room_id
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
			chat_room_id: window.chat_room_id
		},
        url:'/chat/leave/',
    });
}

// attach join and leave events
$(window).load(function(){chat_join()});
$(window).unload(function(){chat_leave()});

