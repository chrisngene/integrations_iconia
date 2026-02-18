from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import models
from api.database import engine

# Access Control
from api.utils.default_sett import default_admin, create_system_functions
from api.routers.v1.user import user_router
from api.routers.v1.authentication import authentication
from api.routers.v1.system_functions import system_functions_router
from api.routers.v1.roles import roles_routers
from api.routers.v1.groups import groups_router

from api.routers.v1.line_clearance import line_clearance_router
from api.routers.v1.vehicles_inspection import (
    vehicles_inspection_router as vehicles_inspection_router,
)
from api.routers.v1.marketing_promotion import (
    marketing_promotion_router as marketing_promotion_router,
)
from api.routers.v1.receipt_ocr import ocr_router
from api.routers.v1.whatsapp_data import whatsapp_data_router


app = FastAPI()

origins = ["http://localhost.tiangolo.com", "https://localhost.tiangolo.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on Aplication StartUp.
models.Base.metadata.create_all(engine)


# Create Admin user on Application Startup if not exsiting.
default_admin()

# Create System Functions
create_system_functions()

app.include_router(authentication.router)
app.include_router(user_router.router)
app.include_router(system_functions_router.router)
app.include_router(roles_routers.router)
app.include_router(groups_router.router)
app.include_router(line_clearance_router.router)
app.include_router(vehicles_inspection_router.router)
app.include_router(marketing_promotion_router.router)
app.include_router(ocr_router.router)
app.include_router(whatsapp_data_router.router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=5000)
