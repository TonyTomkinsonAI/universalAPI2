import azure.functions as func  
from api.app_builder import build_app

# build the fast api app
fastapi_app = build_app()

# return using an ASGI funtion app wrapper
app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
