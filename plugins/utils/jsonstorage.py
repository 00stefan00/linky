from jsonstore import JsonStore 

def add(server_id, key, value):
    store = JsonStore(str(server_id) + ".json")
    store[key] = value

def remove(server_id, key):
    store = JsonStore(str(server_id) + ".json")
    del store[key]
    store._save()

def get(server_id, key):
    store = JsonStore(str(server_id) + ".json")
    return store[key]

def initialize_dict(server_id, list_key):
    store = JsonStore(str(server_id) + ".json")
    exec("store.{} = {}").format(list_key, {})

def add_to_dict(server_id, list_key, key, value):
    store = JsonStore(str(server_id) + ".json")
    store["{}.{}".format(list_key, key)] = value

def remove_from_dict(server_id, list_key, key):
    store = JsonStore(str(server_id) + ".json")
    del store["{}.{}".format(list_key, key)]
    store._save()
