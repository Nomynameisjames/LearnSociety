from functools import wraps
from redis import Redis
from typing import Callable, Dict, List, Union
import json

"""
    decorator caches the result of a method for a given amount of time.
    The cache key is generated from the method name and its arguments.
    The cache is stored in a Redis database.
"""


def cached(timeout=None) -> Callable:
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs) -> str:
            key = f"{str(args)}"
            result = self._cache.get(key)
            if result is not None:
                return result.decode('utf-8')
            else:
                result = method(self, *args, **kwargs)
                self._cache.set(key, json.dumps(result))
                if timeout:
                    self._cache.expire(key, timeout)
                return result
        return wrapper
    return decorator


class Cache:
    """
        Cache class that uses Redis as a database.
        The cache is stored in a Redis database.
    """
    def __init__(self):
        self._cache = Redis(host='localhost', port=6379, db=0)

    """
        Methods for retreiving a data from the cache. based on the key.
    """

    def get(self, key: str):
        return self._cache.get(key)

    """
        Methods for retreiving a data from the cache dictionary object
        based on the key.
    """
    def get_dict(self, redis_key: str, inner_key: str) -> Dict:
        value = self._cache.hget(redis_key, inner_key)
        if value:
            return json.loads(value)
        else:
            return {}

    """
        Methods for retreiving a data from the cache list object
        based on the key.
    """
    def get_list(self, key: str) -> List:
        result = self.get(key)
        if result is not None:
            return json.loads(result)
        return []

    def get_list_dict(self, key: str) -> List:
        """
            Get all items from a list of dictionaries
        """
        result = self._cache.lrange(key, 0, -1)
        if result is not None:
            return [json.loads(item.decode('utf-8')) for item in result]
        return []

    def update_list_dict(self, key: str, idx: int, value: Dict) -> None:
        """
            Update a list of dictionaries at a specific index
        """
        self._cache.lset(key, idx, json.dumps(value))

    """
        method deletes a key from the cache.
    """
    def delete(self, key: str) -> int:
        return self._cache.delete(key)

    """
        method deletes an item key from the cache dictionary object
        by access the data via its key and then deleting the item key.
    """
    def delete_list_dict_item(self, key: str, index: int, item_key: str)\
            -> Union[bool, None]:
        try:
            item = self._cache.lindex(key, index)
            if item is None:
                return False
            else:
                item_dict = json.loads(item)
                if item_key in item_dict:
                    # Delete the key-value pair from the dictionary
                    del item_dict[item_key]
                    # Convert the modified dictionary back to JSON
                    updated_item = json.dumps(item_dict)
                    # Update the Redis list with the modified item
                    self._cache.lset(key, index, updated_item)
                    return True
        except Exception as e:
            print(f"the following error occured: {e}")
            return False

    """
        method deletes an item from the cache list object
        by access the data via its key and then deleting the item.
    """
    def delete_list_item(self, key: str, item: str) -> Union[bool, None]:
        try:
            list_of_items = self.get_list(key)
            if item in list_of_items:
                list_of_items.remove(item)
                self.set_list(key, list_of_items)
                return True
            return False
        except Exception as e:
            print(f"the following error occured: {e}")
            return False

    """
        method checks if a key exists in the redis database
    """
    def exists(self, key: str) -> int:
        return self._cache.exists(key)

    """
        method creates a new key in the redis database with a value
    """
    def set(self, key: str, value: str) -> Union[bool, None]:
        return self._cache.set(key, value)

    """
        method creates a new key in the redis database with a list of values
    """
    def set_list(self, key: str, values: List) -> Union[bool, None]:
        for value in values:
            self._cache.lpush(key, value)

    def set_list_dict(self, key: str, values: List[Dict]) -> Union[bool, None]:
        community = self.get_list_dict(key)
        unique_keys = set()
        try:
            if community:
                for item in community:
                    unique_keys.add(next(iter(item.keys())))
            for value in values:
                get_key = next(iter(value.keys()))
                if get_key not in unique_keys:
                    self._cache.lpush(key, json.dumps(value))
                    unique_keys.add(get_key)
                    return True
        except Exception as e:
            print(f"the following error occured: {e}")
            return False

    """
        method creates a new key in the redis database with a dictionary
        of values and uses the cacheed decorator to set the key with a timeout
    """

    def set_dict(self, key: str, value: Dict, ex=400) -> None:
        encoded_value = {k: json.dumps(v) for k, v in value.items()}
        self._cache.hmset(key, encoded_value)
        self._cache.expire(key, ex)

    """
        method creates a new key in the redis database with a value
        and uses the cacheed decorator to set the key with a timeout
    """
    @cached(timeout=86400)
    def set_cache(self, key: str, value: Union[int, str], ex=86400)\
            -> Union[bool, None]:
        if isinstance(value, bool):
            value = int(value)
        elif isinstance(value, dict):
            value = str(value)
        return self._cache.set(key, value, ex)
