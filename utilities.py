import json

def validate_json(json_data_str:str) -> bool:
    try:
        json.loads(json_data_str)
    except json.JSONDecodeError:
        
        return False

    return True