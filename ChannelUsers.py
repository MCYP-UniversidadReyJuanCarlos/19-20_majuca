import configparser
import json
import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
    PeerChannel
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)


async def main(phone):
    await client.start(phone=phone)
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    user_input_channel = input("Enter entity (telegram URL or entity id): ")

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    participants = await client.get_participants(my_channel)

    all_user_details = []

    for participant in participants:
        photos = await client.get_profile_photos(entity=participant.id)
        for photo in photos:
            await client._download_photo(photo, file=my_channel.title + '/photos/' + str(
                participant.id) + '/' + str(photos.index(photo)),
                                         date=None,
                                         thumb=-1, progress_callback=None)
        all_user_details.append(
            {"id": participant.id, "first_name": participant.first_name, "last_name": participant.last_name,
             "user": participant.username, "phone": participant.phone, "is_bot": participant.bot})

    with open(my_channel.title + '/user_data.json', 'w') as outfile:
        json.dump(all_user_details, outfile)


with client:
    client.loop.run_until_complete(main(phone))
