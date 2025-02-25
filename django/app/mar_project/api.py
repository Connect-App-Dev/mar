from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from mar.api import router as mar_router
from django.contrib.admin.views.decorators import staff_member_required
from ninja_jwt.authentication import JWTAuth
from django.conf import settings

if settings.DEBUG:
    api = NinjaExtraAPI()
else:
    api = NinjaExtraAPI(docs_decorator=staff_member_required)

api.register_controllers(NinjaJWTDefaultController)
api.add_router("/mar/", mar_router, auth=JWTAuth())