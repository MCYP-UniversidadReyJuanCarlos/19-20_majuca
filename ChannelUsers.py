import configparser

from pymongo import MongoClient
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import (
    PeerChannel
)

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
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

    my_channel = await client.get_entity(entity)

    participants = await client.get_participants(my_channel)

    if participants:
        db_client = MongoClient(uri)
        if str(my_channel.id) not in db_client.list_database_names():
            database_participants = db_client[str(my_channel.id)]
        else:
            database_participants = db_client.get_database(str(my_channel.id))
            print("The database already exists")
        for participant in participants:
            if str(participant.id) not in database_participants.list_collection_names():
                participant_collection = database_participants[str(participant.id)]
            else:
                participant_collection = database_participants.get_collection(str(participant.id))
                print("The collection of the participant already exists")
            participant_data = {"_id": participant.id, "type": "participant", "first_name": participant.first_name,
                                "last_name": participant.last_name,
                                "username": participant.username, "phone": participant.phone, "is_bot": participant.bot}
            if participant_collection.find_one({"type": "participant"}) is None:
                participant_collection.insert_one(participant_data)
            photos = await client.get_profile_photos(entity=participant.id)
            for photo in photos:
                if participant_collection.find_one({"_id": photo.id, "type": "photo"}) is None:
                    photo_json = {"_id": photo.id, "type": "photo", "date": photo.date}
                    participant_collection.insert_one(photo_json)
            # await client._download_photo(photo, file=my_channel.title + '/photos/' + str(
            #     participant.id) + '/' + str(photos.index(photo)),
            #                              date=None,
            #                              thumb=-1, progress_callback=None)
    # with open(my_channel.title + '/user_data.json', 'w') as outfile:
    #     json.dump(all_user_details, outfile)

    else:
        print("We can not get any participant")


with client:
    client.loop.run_until_complete(main(phone))
