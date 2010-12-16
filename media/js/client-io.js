
$(document).ready(function(){
	
	var settings = window.chat_settings || {};
	
	var conn_id = settings.conn_id;
	var debug = settings.debug;
	
	
	var nick = settings.nick;
	var room = settings.room;
	var port = settings.port;
	var host = settings.host;
	var socket_lib = settings.socket_lib;
	
	var rooms = {};
	
	
	io.setPath(socket_lib);
	var socket = new io.Socket(host, {rememberTransport: false, port: port});
	socket.connect();
	
	function startswith(start, str){
		return String(str).indexOf(start) >= 0;
	}
	
	function get_message(message){
		var msg = message.msg;
		var result = "";
		if(startswith('/hello', msg)){
			var s = String(msg).replace('/hello ', '');
			result = '';
		}
	
		if(startswith('/join', msg)){
			var s = String(msg).replace('/join ', 'Вошел пользователь - ');
			result = s;
		}
	
		if(startswith('/quit', msg)){
			var s = String(msg).replace('/quit ', 'Вышел пользователь - ');
			result = s;
		}
		
		if(startswith('/msg', msg)){
			var s = String(msg).replace('/msg ', message.from + ": " || '');
			result = s;
		}
		
		
		return "<p>"+result+"<p>"
	}
	
	socket.on('message', function(message){
		message = JSON.parse(message);
		var data = message.msg.split(" ");
		var text = message.msg;
	
		$('#chat').append(get_message(message));
	});
	
	socket.on('connect', function(){
		socket.send("/nick " + nick);
		socket.send("/join " + room);
	});
	
	
	
	$('#comment').submit(function(event){
		
		var message = $("#message").val();
		socket.send("/msg " + room + " " + message);
		$('#message').val("");
		//$('#chat').append("<p>"+message+"<p>");
		event.preventDefault();
		return false;
	});
});

