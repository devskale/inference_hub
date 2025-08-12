
import json_repair


def cleanify_json(json_string):
    """
    Cleans AI-generated JSON strings by removing extraneous formatting like triple backticks and ensuring valid JSON.
    """
    # Remove triple backticks and any surrounding whitespace
    # good_json_string = repair_json(json_string)
    decoded_object = json_repair.repair_json(json_string, return_objects=True)
    return decoded_object
