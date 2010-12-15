var http = require("http"),
    //ws = require("./lib/node-websocket-server/lib/ws"),
    io = require('./lib/socket-io-node'),
    sys = require("sys"),
    fs = require("fs"),
    url = require('url'),
    nicks = {},
    rooms = {},
    ignore_uniq = false,
    allowed_domains = ["localhost:8090", 'modnoemesto.ru:8090'];



var send404 = function(res) {
    res.writeHead(404);
    res.write('404');
    res.end();
};

var json = JSON.stringify;

function HTMLEncode(wText){
    if(typeof(wText) != "string"){
        wText = String(wText);
    }
	
    wText=wText.replace(/</g, "&lt;");
    wText=wText.replace(/>/g, "&gt;");
	
    return wText;
};

function sendNicksList(client, room) {
    var n = [];
    for(key in nicks) {
        try {
            if (nicks[key] && nicks[key]["rooms"] && nicks[key]["rooms"].indexOf(room) >= 0) {
				n.push(key + ":" + nicks[key]["nick"]);
			}
        } catch(e) { 
			sys.puts(e); 
		} 
    } 
    broadCast(client, room, "/list " + n.join(","));
}

function nick_has_room(nick, room){
	return nick && nick["rooms"] && 
		   nick["rooms"].indexOf(room) >= 0;
}

function broadCast(client, room, msg) {    
    var n = [];
	var sid = client.sessionId;
	
	sys.puts(">>> broadCast: room="+room+" message="+msg);
	
    for(var key in nicks) {
        try {
            if(nicks[key] && nicks[key]["rooms"] && nicks[key]["rooms"].indexOf(room) >= 0) {
                sys.puts(key + " > " + msg);
                var n = "";
				
                if(nicks[sid]){
					n = nicks[sid]["nick"];
				}
				 
                client.send_to(key, json({ 
						msg: HTMLEncode(msg), 
						room: HTMLEncode(room), 
						from: HTMLEncode(n) 
					})
				);            
            }
        } catch(e) { 
			sys.puts(e); 
		}
    }    
}

function uniqNick(client, nick) {
    var test = true;
    for(key in nicks) {
        if(nicks[key] && nicks[key]["nick"] == nick) test = false;
    } 
    return test;
}

var httpServer = http.createServer(function(req, res) { 
    if(req.method == "HEAD") {
        res.end();
    } else {
        var path = url.parse(req.url).pathname;
        if(path == "/") path = "/client-io.html";
        switch (path) {
            default:
                if (/\.(js|html|swf|wav|css|png)$/.test(path)){
                    try {
                    
                        var ct = "text/html";
                        var mode = "utf8";
                    
                        if(path.substr(-4) === '.swf') {
                            ct = "application/x-shockwave-flash";
                            mode = "binary";
                        }
                        if(path.substr(-3) === '.js') ct = "text/javascript";                            
                        if(path.substr(-4) === '.css') ct = "text/css";                            
                        if(path.substr(-4) === '.wav') {
                            ct = "audio/x-wav";
                            mode = "binary";
                        }
                        if(path.substr(-4) === '.png') {
                            ct = "image/png";
                            mode = "binary";
                        }
                        res.writeHead(200, {'Content-Type': ct });
                        res.write(fs.readFileSync(__dirname + path, mode), mode);
                        res.end();
                    } catch(e){ 
                        send404(res); 
                    }             
                    break;
                }
                send404(res);
                break;
        }
    } 
});

httpServer.listen(80);

var socket = io.listen(httpServer);

socket.on("connection", function(client){
    
    sys.puts("<"+client.sessionId+"> connected");
    
    client.on("disconnect", function() {
        var u_rooms = [];
		var sid = client.sessionId.toString();
        if(nicks[sid] != undefined){
			u_rooms = nicks[sid]["rooms"];
		}
		 
        sys.puts("<"+sid+"> disconnected");
		
        for(var room in u_rooms) {
            broadCast(client, u_rooms[room], "/quit " + nicks[sid]["nick"]); 
        }
        nicks[sid] = undefined;

    });
    
    client.on("message", function(message) {
        var allowed = false;
		/*
        for(domain in allowed_domains) {
            if(allowed_domains[domain] == client.request.headers.host){
				allowed = true;
			} 
        }
        */
        allowed = true;

        sys.puts("Message: "+message);
        if(allowed) {
            var msg = message.split(" ");
            sys.puts(msg);
			
			var sid = client.sessionId.toString();
			
            switch (msg[0]) { 
                case "/whoami": 
                    client.send(json({ 
							msg: "/hello " +  sid
						})
					);
                    break;
					
                case "/nick":
					var nick = msg.slice(1).join(" ").trim();
                    if (ignore_uniq || uniqNick(client, nick)) {
						if (nicks[sid] == undefined) {
							nicks[sid] = {};
						}
						
						nicks[sid]["nick"] = nick;
						sys.puts("Nick added: - " + nick);
//						for(var i in nicks){
//							if(nicks[i].hasOwnProperty("nick")){
//								sys.puts("nicks: "+nicks[i]["nick"]);
//							}
//							
//						}
//						client.send(json({
//								msg: "/your_nick " + nick
//							})
//						);
						
					} else {
//						client.send(json({ 
//								msg: "/notice Login " + nick + " already used"
//							})
//						);
					}
                    break;
					
                case "/join":
					var room = msg.slice(1).join(" ");
				
                    if(nicks[sid] == undefined){
						nicks[sid] = {};
					}
					
                    if(nicks[sid]["rooms"] == undefined){
						nicks[sid]["rooms"] = [];
					}
					
                    nicks[sid]["rooms"].push(room);
                    broadCast(client, room, 
						"/join " + nicks[sid]["nick"]);
                    break;
					
                case "/msg":
					var message = msg.slice(2).join(" ");
					var room = msg[1];
					
                    broadCast(client, room, "/msg " + message);
                    break;
					
                case "/list":
                    sendNicksList(client, msg.slice(1).join(" "));
					
                case "/writing":
                    //broadCast(client, msg[1], "/writing " + client.sessionId);
                    break;
					
                case "/pm":
                    try {
                        client.send_to(msg[1], json({ msg: HTMLEncode("/msg " + msg.slice(2).join(" ")), room: HTMLEncode("/pm"), from: HTMLEncode(client.sessionId), name: HTMLEncode(nicks[client.sessionId]["nick"]), toname: HTMLEncode(nicks[client.sessionId]["nick"]) }));
                        client.send_to(client.sessionId, json({ msg: HTMLEncode("/msg " + msg.slice(2).join(" ")), room: HTMLEncode("/pm"), from: HTMLEncode(client.sessionId), name: HTMLEncode(nicks[msg[1]]["nick"]), to: msg[1], toname: HTMLEncode(nicks[client.sessionId]["nick"]) }));
                    } catch(e) { sys.puts(e); }
                    break;
					
                case "/part":
                    var pos = nicks[client.sessionId]["rooms"].indexOf(msg.slice(1).join(" "));                
                    if(pos >= 0) nicks[client.sessionId]["rooms"].splice(pos,1);
                    sendNicksList(client, msg.slice(1).join(" "));
                    broadCast(client, msg.slice(1).join(" "), "/part " + client.sessionId);
                    break;
					
                case "/sessionId":
                    ignore_uniq = true;
                    client.sessionId = msg[1];
                    client.send(json({ msg: "/your_id " + msg[1] }));                    
                    break;
					
                default: 
                    break;
					
                break;
            } // Switch
        } // If allowed
    });
});
