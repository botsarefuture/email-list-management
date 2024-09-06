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
        return {
            key: convert_object_ids_to_strings(value) for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_object_ids_to_strings(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
