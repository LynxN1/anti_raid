import amino
import threading
import time

from termcolor import colored


client = amino.Client()

email = input("Email: ")
password = input("Password: ")
client.login(email=email, password=password)

sub_clients = client.sub_clients(start=0, size=100)
for x, name in enumerate(sub_clients.name, 1):
    print(f"{x}. {name}")
com_id = sub_clients.comId[int(input("Выберите сообщество: ")) - 1]
sub_client = amino.SubClient(comId=str(com_id), profile=client.profile)


admins = {}


@client.callbacks.event("TYPE_USER_SHARE_EXURL")
@client.callbacks.event("TYPE_USER_SHARE_USER")
@client.callbacks.event("on_voice_chat_not_answered")
@client.callbacks.event("on_voice_chat_not_cancelled")
@client.callbacks.event("on_voice_chat_not_declined")
@client.callbacks.event("on_video_chat_not_answered")
@client.callbacks.event("on_video_chat_not_cancelled")
@client.callbacks.event("on_video_chat_not_declined")
@client.callbacks.event("on_avatar_chat_not_answered")
@client.callbacks.event("on_avatar_chat_not_cancelled")
@client.callbacks.event("on_avatar_chat_not_declined")
@client.callbacks.event("on_delete_message")
@client.callbacks.event("on_group_member_join")
@client.callbacks.event("on_group_member_leave")
@client.callbacks.event("on_chat_invite")
@client.callbacks.event("on_chat_background_changed")
@client.callbacks.event("on_chat_title_changed")
@client.callbacks.event("on_chat_icon_changed")
@client.callbacks.event("on_voice_chat_start")
@client.callbacks.event("on_video_chat_start")
@client.callbacks.event("on_avatar_chat_start")
@client.callbacks.event("on_voice_chat_end")
@client.callbacks.event("on_video_chat_end")
@client.callbacks.event("on_avatar_chat_end")
@client.callbacks.event("on_chat_content_changed")
@client.callbacks.event("on_screen_room_start")
@client.callbacks.event("on_screen_room_end")
@client.callbacks.event("on_text_message_force_removed")
@client.callbacks.event("on_chat_removed_message")
def handle_messages(data):
    content = data.message.content
    media_type = data.message.mediaType
    if content and media_type == 0:
        chatid = data.message.chatId
        userid = data.message.author.userId
        nickname = data.message.author.nickname
        threading.Thread(target=exploit_message, args=[chatid, userid, nickname]).start()


def exploit_message(chatid: str, userid: str, nickname: str):
    if admins.get(chatid) is None:
        set_admins(chatid)
    if userid not in admins[chatid]:
        try:
            sub_client.kick(userId=userid, chatId=chatid, allowRejoin=False)
            sub_client.send_message(chatId=chatid,
                                    message=f"{nickname} был удален из чата за отправку сообщения с измененным типом")
        except amino.exceptions.AccessDenied:
            pass
        except Exception as e:
            print(e)
    print(colored(f"{nickname} отправил сообщение с измененным типом в чате {chatid}", "red"))


def set_admins(chatid: str):
    chat = sub_client.get_chat_thread(chatId=chatid)
    if chat.type != 0:
        admins[chatid] = [*chat.coHosts, chat.author.userId]
    else:
        admins[chatid] = [chat.author.userId]


def restart():
    while True:
        time.sleep(120)
        count = 0
        for i in threading.enumerate():
            if i.name == "restart_thread":
                count += 1
        if count <= 1:
            print("Restart")
            client.socket.close()
            client.socket.start()


if __name__ == '__main__':
    restart_thread = threading.Thread(target=restart)
    restart_thread.setName("restart_thread")
    restart_thread.start()
