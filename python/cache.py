import uuid

from flask import session
from flask_caching import Cache

# Crie a instância aqui, mas não inicialize ainda
cache = Cache()

def init_cache(app):
    """
    Chame esta função no app principal para inicializar o cache
    com as configurações desejadas.
    """
    cache.init_app(app, config={
        "CACHE_TYPE": "SimpleCache",       # ou RedisCache, FileSystemCache etc.
        "CACHE_DEFAULT_TIMEOUT": 1300      # 30 min
    })

def session_key(key: str) -> str:
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return f"{session['sid']}:{key}"