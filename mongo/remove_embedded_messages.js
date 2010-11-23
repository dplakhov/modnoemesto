db.user.update({}, { $unset : { msg_inbox: 1, msg_inbox_count: 1 , msg_sent: 1, msg_sent_count: 1, unread_msg_count: 1} })
