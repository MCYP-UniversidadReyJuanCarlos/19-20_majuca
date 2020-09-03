import configparser
import pickle
import re

from pymongo import MongoClient
from pymongo.collection import Collection
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, UserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import (
    PeerChannel, Photo, User, Message
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
message_limit = config['Telegram']['message_limit']
uri = config['Mongo']['uri']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)


async def main(phone):
    await client.start(phone=phone)
    print("Client Created")
    # Ensure you're authorized
    if not await client.is_user_authorized():
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

    if entity.find("joinchat"):
        entity = re.sub('.*/', '', entity)

    try:
        await client(ImportChatInviteRequest(entity))
    except UserAlreadyParticipantError:
        print("The authenticated user is already a participant of the chat")

    my_channel = await client.get_entity(entity)
    participants = await client.get_participants(my_channel)

    if participants:
        db_client = MongoClient(uri)
        database_participants, participant_collection, photo_collection, message_collection = check_bbdd(db_client, str(
            my_channel.id))
        for participant in participants:
            if participant_collection.find_one({"_id": participant.id}) is None:
                participant_data = map_participant(participant)
                participant_collection.insert_one(participant_data)
            await download_participant_photos(participant, photo_collection, my_channel.title + '/photos/' + str(
                participant.id) + '/')
        messages = await client.get_messages(my_channel, limit=int(message_limit))
        for message in messages:
            if isinstance(message, Message) and message_collection.find_one({"_id": message.id}) is None:
                message_json = map_message(message)
                message_collection.insert_one(message_json)

    else:
        print("We can not get any participant")


def map_participant(participant: User):
    participant_bytes = pickle.dumps(participant)
    participant_json = {"_id": participant.id, "first_name": participant.first_name,
                        "last_name": participant.last_name,
                        "username": participant.username, "phone": participant.phone,
                        "is_bot": participant.bot, "entity": participant_bytes}
    return participant_json


def map_photo(photo: Photo, participant_id: int):
    photo_bytes = pickle.dumps(photo)
    photo_json = {"_id": photo.id, "participantId": participant_id, "date": photo.date, "entity": photo_bytes}
    return photo_json


def map_message(message):
    message_json = {"_id": message.id, "date": message.date, "senderId": message.sender.id,
                    "text": message.message}
    return message_json


async def download_photo_local(photo, route):
    await client._download_photo(photo, file=route,
                                 date=None,
                                 thumb=-1, progress_callback=None)


async def download_participant_photos(participant: User, photo_collection: Collection, route: str):
    photos = await client.get_profile_photos(entity=participant.id)
    for photo in photos:
        if photo_collection.find_one({"_id": photo.id, "participantId": participant.id}) is None:
            photo_json = map_photo(photo, participant.id)
            photo_collection.insert_one(photo_json)
            ''' With these lines we can get a entity photo of bbdd and download
            result = participant_collection.find_one({"_id": photo.id})
            print(result['entity'])
            photo_load = pickle.loads(result['entity'])
            download_photo_local(photo, route + str(photos.index(photo)))
            '''


def check_bbdd(db_client: MongoClient, channel_id: str):
    if channel_id not in db_client.list_database_names():
        database_participants = db_client[channel_id]
    else:
        database_participants = db_client.get_database(channel_id)
        print("The database already exists")
    if "Participants" not in database_participants.list_collection_names():
        participant_collection = database_participants['Participants']
    else:
        participant_collection = database_participants.get_collection('Participants')
    if "Photos" not in database_participants.list_collection_names():
        photo_collection = database_participants['Photos']
    else:
        photo_collection = database_participants.get_collection('Photos')
    if "Messages" not in database_participants.list_collection_names():
        message_collection = database_participants['Messages']
    else:
        message_collection = database_participants.get_collection('Messages')
    return database_participants, participant_collection, photo_collection, message_collection


with client:
    client.loop.run_until_complete(main(phone))
