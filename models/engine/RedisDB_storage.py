from functools import wraps
from redis import Redis
from typing import Callable, Dict, List
import json

"""
    decorator caches the result of a method for a given amount of time.
    The cache key is generated from the method name and its arguments.
    The cache is stored in a Redis database.
"""
def cached(timeout=86400):
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            key = f"{method.__name__}:{str(args)}:{str(kwargs)}"
            result = self._cache.get(key)
            if result is not None:
                return result.decode('utf-8')
            else:
                result = method(self, *args, **kwargs)
                self._cache.set(key, json.dumps(result), ex=timeout)
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
        self._cache.flushdb()

    """
        Methods for retreiving a data from the cache. based on the key.
    """
    def get(self, key):
        return self._cache.get(key)
    
    """
        Methods for retreiving a data from the cache dictionary object
        based on the key.
    """
    def get_dict(self, key) -> Dict:
        value = self.get(key)
        if value is None:
            return {}
        return json.loads(value)
    
    """
        Methods for retreiving a data from the cache list object
        based on the key.
    """
    def get_list(self, key) -> List:
        result = self.get(key)
        if result is not None:
            return json.loads(result)
        return []
    
    """
        method deletes a key from the cache.
    """
    def delete(self, key):
        return self._cache.delete(key)
    
    """
        method deletes an item key from the cache dictionary object
        by access the data via its key and then deleting the item key.
    """
    def delete_list_dict_item(self, key, item_key):
        list_of_dicts = self.get_list(key)
        for d in list_of_dicts:
            if item_key in d:
                del d[item_key]
                self.set_list(key, list_of_dicts)
                return True
        return False
    """
        method deletes an item from the cache list object
        by access the data via its key and then deleting the item.
    """
    def delete_list_item(self, key, item):
        list_of_items = self.get_list(key)
        if item in list_of_items:
            list_of_items.remove(item)
            self.set_list(key, list_of_items)
            return True
        return False

    """
        method checks if a key exists in the redis database
    """
    def exists(self, key):
        return self._cache.exists(key)

    """
        method creates a new key in the redis database with a value
    """
    def set(self, key, value):
        return self._cache.set(key, value)

    """
        method creates a new key in the redis database with a list of values
    """
    def set_list(self, key, values):
        for value in values:
            self._cache.lpush(key, value)

    """
        method creates a new key in the redis database with a dictionary
        of values and uses the cacheed decorator to set the key with a timeout
    """
    @cached(timeout=86400)
    def set_dict(self, key, value: Dict, ex=86400):
        self._cache.set(key, json.dumps(value), ex)

    """
        method creates a new key in the redis database with a value
        and uses the cacheed decorator to set the key with a timeout
    """
    @cached(timeout=86400)
    def set_cache(self, key, value, ex=86400):
        if isinstance(value, bool):
            value = int(value)
        elif isinstance(value, dict):
            value = str(value)
        return self._cache.set(key, value, ex)
