import json

def get_json_settings():
    with open('app/config.json', 'r') as file:
        settings = json.load(file)
    return settings

def set_json_settings(settings: dict):
    with open('app/config.json', 'w') as file:
        json.dump(settings, file, indent=4)