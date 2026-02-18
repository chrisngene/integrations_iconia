from fastapi import APIRouter, Depends, status, HTTPException
from api.routers.v1.marketing_promotion import marketing_promotion_repository as vi
from sqlalchemy.orm import Session
from api import service, database
from api.routers.v1.authentication.auth_outh2 import get_current_user
from typing import List

router = APIRouter(prefix="/api/v1/marketing_promotion", tags=["Marketing Promotion"])


# @router.get(
#     "/first",
#     status_code=status.HTTP_200_OK,
#     response_model=List[service.MarketingPromotion],
# )
# def get_all_marketing_promotions_1(db: Session = Depends(database.get_db)):
#     return vi.get_all_1(db)


# @router.get(
#     "/second",
#     status_code=status.HTTP_200_OK,
#     response_model=List[service.MarketingPromotion],
# )
# def get_all_marketing_promotions_2(db: Session = Depends(database.get_db)):
#     return vi.get_all_2(db)


names = [
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
]


for i, name in enumerate(names, start=1):
    # Get the correct repository function by name dynamically
    repo_func_name = f"get_all_marketing_promotions_{i}"
    repo_func = getattr(vi, repo_func_name, None)

    if repo_func is None:
        # Optional: skip or raise if not implemented in vi
        continue

    async def endpoint(db: Session = Depends(database.get_db), func=repo_func):
        return func(db)

    router.add_api_route(
        f"/{name}",
        endpoint,
        methods=["GET"],
        status_code=status.HTTP_200_OK,
        response_model=List[service.MarketingPromotion],
        name=repo_func_name,
    )


# Update Checkout product quantity in the Marketing Promotion List
@router.post("/update-product-qty/{instance_id}", status_code=status.HTTP_200_OK)
def update_product_quantity(
    instance_id: int,
    db: Session = Depends(database.get_db),
):
    return vi.update_product_quantity(instance_id, db)
