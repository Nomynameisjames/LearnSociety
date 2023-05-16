#!/usr/bin/python3
import os

storage = None
redis_storage = None

storage_type = os.environ.get('STORAGE_TYPE')
storage_type2 = os.environ.get('STORAGE_TYPE2')

if storage_type == 'mysqlDB':
    """
        creates a unique FileStorage instance for your application
        using the mysqlDB storage engine
    """
    from models.engine.DB_storage import DBstorage
    storage = DBstorage()
    storage.reload()

if storage_type2 == 'redisDB':
    """
        creates a unique FileStorage instance for your application
        using the redisDB storage engine for caching purposes
    """
    from models.engine.RedisDB_storage import Cache
    redis_storage = Cache()
else:
    raise Exception("Invalid storage engine")
