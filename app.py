import os
from flask import Flask, render_template
from azure.cosmos import CosmosClient

app = Flask(__name__)

url = 'https://monitor-db.documents.azure.com:443/'
key = os.environ.get('COSMOS_DB_KEY')
client = CosmosClient(url, credential=key)
database_name = 'Monitor'
container_name = 'Users'

def format_user_data(user_data):
    name = user_data.get('name', '')
    surname = user_data.get('surname', '')
    return f'Witaj {name} {surname}'

def get_user_data(user_id):
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    query = (f"SELECT c.na"
             f"me, c.surname FROM c WHERE c.id = '{user_id}'")
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    return items

@app.route('/')
def hello_world():
    # user_id = 1
    # user_data = get_user_data(user_id)
    # return format_user_data(user_data[0])
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
