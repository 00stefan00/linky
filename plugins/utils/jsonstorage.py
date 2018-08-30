from jsonstore import JsonStore 

def add(server_id, key, value):
	store = JsonStore(str(server_id) + ".json")
	store[key.fget()] = value

def remove(server_id, key):
	store = JsonStore(str(server_id) + ".json")
	del store[key.fget()]

def get(server_id, key):
	store = JsonStore(str(server_id) + ".json")
	return store[key.fget()]

	