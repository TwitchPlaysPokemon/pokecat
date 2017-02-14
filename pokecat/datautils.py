
import json
from operator import itemgetter

from Levenshtein import ratio


def build_from_json_dict(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        dict_ = json.load(f)
    for id_, name in dict_.items():
        yield {
            "id": int(id_),
            "name": name,
            "description": "",
        }

def build_from_json_list(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        list_ = json.load(f)
    for i, item in enumerate(list_):
        yield {
            "id": i,
            "name": item,
            "description": "",
        }

def load_from_json_list(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_exact(lst, id_or_name, namegetter=itemgetter("name")):
    """
    Gets something by id or name, which has to match exactly.
    Matches by id if `id_or_name` is int, by name otherwise.
    Either returns the matching item, or None if none was found.
    """
    for item in lst:
        if not item:
            continue  # null item, for lists having nothing as id 0 for example
        if isinstance(id_or_name, int) and item["id"] == id_or_name:
            return item
        if id_or_name == namegetter(item):
            return item
    return None

def find_similar(lst, name, min_similarity=0.75, namegetter=itemgetter("name")):
    """
    Finds something by name, which doesn't have to be an exact match.
    Returns a dict {id: item} which items that satisfy the needed similarity.

    If the dict is empty, no items matched. If it has more than 1 item,
    the supplied item's name should be considered ambiguous.
    """
    entries = {}
    highest_similarity = 0
    for index, item in enumerate(lst):
        if not item or not item["name"]:
            continue  # null item, for lists having nothing as id 0 for example
        actual_name = namegetter(item)
        id_ = item["id"]
        similarity = ratio(name.lower(), actual_name.lower())
        if similarity == 1.0:
            # full match, just return this
            return {id_: item}
        if similarity - highest_similarity > 0.1:
            # the rest isn't close enough, ditch them
            entries.clear()
        if similarity >= min_similarity and highest_similarity - similarity < 0.1:
            entries[id_] = item
        highest_similarity = max(highest_similarity, similarity)
    return entries
