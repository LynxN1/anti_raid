import time

import amino_

client = amino_.Client("226001BFCBBC40B661C61281F7C1E716660E3909B5DAA30D26B63412EA70B7AD28B8CACF832E6487F4")
client.login(email="", password="")  # Логин и пароль от аккаунта бота
print("Авторизация прошла успешно")
sub_client = amino_.SubClient(comId="", profile=client.profile)  # Айди сообщества
print("Мониторинг чатов...")


WARNS = []
ANTI_SPAM = {}
JOIN_LEAVE_DETECTOR = {}


def on_message(data):
    user_id = data.message.author.userId
    if user_id != client.userId:
        msg_type = data.message.type
        if msg_type != 0:
            media_type = data.message.mediaType
            content = data.message.content
            if content is not None and media_type == 0:
                sub_client.kick(chatId=data.message.chatId, userId=user_id, allowRejoin=False)
                print(f"{user_id} удален из чата за отправку системного сообщения")


@client.event("on_image_message")
@client.event("on_text_message")
def on_antispam(data):
    user_id = data.message.author.userId
    print(f"[{data.message.author.nickname}]: {data.message.content}")
    if user_id != client.userId:
        if ANTI_SPAM.get(user_id) is None:
            ANTI_SPAM[user_id] = int(time.time())
        elif int(time.time()) - ANTI_SPAM[user_id] <= 0.5:
            if WARNS.count(user_id) >= 4:
                sub_client.kick(userId=user_id, chatId=data.message.chatId, allowRejoin=False)
                print(f"{user_id} удален из чата за спам")
                for i in WARNS:
                    if i == user_id:
                        WARNS.remove(user_id)
            else:
                WARNS.append(user_id)
        elif int(time.time()) - ANTI_SPAM[user_id] > 1:
            ANTI_SPAM[user_id] = int(time.time())
            for i in WARNS:
                if i == user_id:
                    WARNS.remove(user_id)


@client.event("on_group_member_join")
@client.event("on_group_member_leave")
def on_join_leave(data):
    user_id = data.message.author.userId
    if user_id != client.userId:
        if JOIN_LEAVE_DETECTOR.get(user_id) is None:
            JOIN_LEAVE_DETECTOR[user_id] = int(time.time())
        elif int(time.time()) - JOIN_LEAVE_DETECTOR[user_id] <= 1:
            sub_client.kick(userId=user_id, chatId=data.message.chatId, allowRejoin=False)
            print(f"{user_id} удален из чата за спам входом/выходом из чата")
        elif int(time.time()) - JOIN_LEAVE_DETECTOR[user_id] > 1:
            JOIN_LEAVE_DETECTOR[user_id] = int(time.time())


methods = []
for x in client.chat_methods:
    methods.append(client.event(client.chat_methods[x].__name__)(on_message))
