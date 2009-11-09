from plone.memoize import volatile
from plone.memoize.ram import store_in_cache

def cache(get_key, dependencies=None):
    if dependencies is not None:
        
    return volatile.cache(get_key, get_cache=store_in_cache)
