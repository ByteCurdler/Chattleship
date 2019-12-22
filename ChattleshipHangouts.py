from ChattleshipBase import *
import hangups, asyncio, threading

def initClient():
    async def sub_go():
        global cookies, client
        cookies = hangups.get_auth_stdin("./.hangups-auth", True)
        client = hangups.Client(cookies)
        task = asyncio.ensure_future(client.connect())
        on_connect = asyncio.Future()
        client.on_connect.add_observer(lambda: on_connect.set_result(None))
        done, _ = await asyncio.wait(
            (on_connect, task), return_when=asyncio.FIRST_COMPLETED
            )
        await asyncio.gather(*done)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(sub_go(), loop=loop)
    loop.run_until_complete(task)

def getList(client):
    ret = []
    @asyncio.coroutine
    def a(ret):
        user_list,conv_list = (
                    yield from hangups.build_user_conversation_list(client)
        )
        ret += [user_list, conv_list]
    asyncio.get_event_loop().run_until_complete(a(ret))
    return ret

def send_message(client, conv_id, message):
    async def subsend():
        request = hangups.hangouts_pb2.SendChatMessageRequest(
            request_header=client.get_request_header(),
            event_request_header=hangups.hangouts_pb2.EventRequestHeader(
                conversation_id=hangups.hangouts_pb2.ConversationId(
                    id=conv_id
                ),
                client_generated_id=client.get_client_generated_id(),
            ),
            message_content=hangups.hangouts_pb2.MessageContent(
                segment=[
                    hangups.ChatMessageSegment(message).serialize()
                ],
            ),
        )
        await client.send_chat_message(request)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(subsend(),
                                 loop=loop)
    loop.run_until_complete(task)

initClient()
data = getList(client)
users = list(data[0].get_all())
convs = data[1]
email = input("Opponent's email? ")
user = [i for i in users if email in i.emails][0]
conv = [i for i in convs.get_all() if len(i.users) == 2 and user in i.users][0]

new_messages = []

def on_new_message(event):
##    print("event")
    if isinstance(event, hangups.ChatMessageEvent):
        if event.user_id == user.id_:
##            print('received chat message: {!r}'.format(event.text))
            new_messages.append(event.text)

async def receive_messages(client):
    conv.on_event.add_observer(on_new_message)
    await asyncio.sleep(0.5)
    conv.on_event.remove_observer(on_new_message)
    

def get_message():
    global new_messages
    while len(new_messages) == 0:
        asyncio.get_event_loop().run_until_complete(receive_messages(client))
    return new_messages.pop(0)

if __name__ == "__main__":
    inst = Base(
        [
            get_message,
            lambda x: send_message(client, conv.id_, x)
        ],
        [CLI.input, CLI.output]
    )
    inst.play(input("Is first? (Y/n) ").lower().startswith("y"))
