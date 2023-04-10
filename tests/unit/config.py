from os import environ as env

# URLs
URL_FRONTEND = env.get("URL_FRONTEND", default="http://localhost:8000")
URL_BACKEND = env.get("URL_BACKEND", default="http://localhost:8001")
