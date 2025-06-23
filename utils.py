import os

def resource_path(relative_path):
    # Gets absolute path to resource, works for dev and for packaged app
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
