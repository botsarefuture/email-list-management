from bson import ObjectId

def convert_object_ids_to_strings(data):
    """
    Recursively converts all ObjectId instances in JSON-like data to strings.

    Parameters:
    data (any): The JSON-like data containing ObjectId instances.

    Returns:
    any: The JSON-like data with ObjectId instances converted to strings.
    """
    if isinstance(data, dict):
        return {key: convert_object_ids_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_object_ids_to_strings(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


import hashlib

def generate_txt_record(user_id):
    # Create a unique hash from the user ID
    user_hash = hashlib.sha256(user_id.encode()).hexdigest()
    # Format the TXT record
    txt_record = user_hash
    return txt_record
