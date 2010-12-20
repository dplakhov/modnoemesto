from datetime import datetime
import json

from django.shortcuts import render_to_response
from django.http import HttpResponse

#from models import Message

import stomp
from django.conf import settings


def get_destination(request):
    cam_id = request.POST.get("cam_id", "")
#    destination = '/queue/%s' % (cam_id, )
#    destination = '/messages'
    return cam_id
    

def subscribe(request):
    cam_id = request.POST.get("cam_id", "")
    if cam_id in settings.CHAT_CONNECTIONS:
        conn = settings.CHAT_CONNECTIONS[cam_id]
    else:
        conn = stomp.Connection()
        conn.start()
        conn.connect()
        destination = get_destination(request)
        conn.subscribe(destination=destination, ack='auto')
        settings.CHAT_CONNECTIONS[cam_id] = conn
    
    return HttpResponse("ok") 
    
def unsubscribe(request):
    cam_id = request.POST.get("cam_id", "")
    if cam_id in settings.CHAT_CONNECTIONS:
        conn = settings.CHAT_CONNECTIONS[cam_id]
        destination = get_destination(request)
        conn.unsubscribe(destination=destination)
        del settings.CHAT_CONNECTIONS[cam_id]
    
    return HttpResponse("ok")

def send(request):
    user = request.user.get_full_name()
    cam_id = request.POST.get("cam_id", "")
    message = request.POST.get("message", "")
    destination = get_destination(request)
    time = datetime.now()
    
    msg_to_send = json.dumps({
        "user":user,
        "message":message, 
        "time":time.strftime("%H:%S-%d/%m/%Y")
    })
    
    if cam_id in settings.CHAT_CONNECTIONS:
        conn = settings.CHAT_CONNECTIONS[cam_id]
        conn.send(msg_to_send, destination=destination)
        
    return HttpResponse("ok")