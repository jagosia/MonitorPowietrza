import os
from azure.cosmos import CosmosClient

key = os.environ.get('COSMOS_DB_KEY')
url = 'https://monitor-db.documents.azure.com:443/'
client = CosmosClient(url, credential=key)
database_name = 'Monitor'
container_name = 'Users'


def get_user_by_email(email):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = (f"SELECT c.id, c.name,c.lastname, c.email, c.passwordHash, c.phone, c.city, c.notification "
             f"FROM c WHERE c.email = '{email}'")
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(result) == 0:
        return None
    return result[0]


def add_new_user(user):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    container.upsert_item(user)


def get_user_document_by_id(user_id, partition_key):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    return container.read_item(item=user_id, partition_key=partition_key)


def replace_document(user_id, document):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    container.replace_item(item=user_id, body=document)


def get_users_to_notify():
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    query = (f"SELECT * "
             f"FROM c WHERE c.notification = true")
    return  list(container.query_items(query=query, enable_cross_partition_query=True))

def upsert_item(person):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    container.upsert_item(person)