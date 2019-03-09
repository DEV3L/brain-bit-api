def get_json_data(request_json, required_keys):
    if not request_json or \
            not all(keys in request_json for keys in required_keys):
        keys_str = ', '.join(required_keys)
        raise RuntimeError(f'Invalid JSON Request Data: {keys_str}')

    return request_json
