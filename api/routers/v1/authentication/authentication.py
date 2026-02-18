from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api import database, models
from api.libs.hashing import Hash
from api.routers.v1.authentication import auth_token
from api.utils.check_if_authorized import if_authorized


router = APIRouter(tags=["Authentication"], prefix="/login")


@router.post("/")
def login(
    login: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)
):
    # Try to find the user by username OR email
    user = (
        db.query(models.User)
        .filter(
            (models.User.user_username == login.username)
            | (models.User.user_email == login.username)
        )
        .first()
    )

    if not user or not Hash.verify(user.user_password, login.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username/email or password",
        )

    user_roles = if_authorized(user.user_username, db)
    access_token = auth_token.create_access_token(data={"sub": user.user_username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_roles": user_roles,
    }
