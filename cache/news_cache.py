from typing import Dict, List, Any
from conf.redis_conf import get_json_cache, set_cache
import warnings
import functools

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list"


async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


def deprecated(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        warnings.warn(f"{func.__name__} is deprecated and will be removed in a future version.", DeprecationWarning,
                      stacklevel=2)
        return await func(*args, **kwargs)

    return wrapper


@deprecated
async def get_cache_news_list(category_id: int, page: int, size: int, expire: int = 1800):
    category_part = category_id if category_id else "all"
    key = f'{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}'
    return await get_json_cache(key)


@deprecated
async def set_cache_news_list(category_id: int, page: int, size: int, news_list: List[Dict[str, Any]],
                              expire: int = 1800):
    category_part = category_id if category_id else "all"
    key = f'{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}'
    return await set_cache(key, news_list, expire)
