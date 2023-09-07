import azure.functions as func

#from WrapperFunction import app as fastapi_app

#app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)        

from api.app_builder import build_app

fastapi_app = build_app()

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)