from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union, Dict, Any
from datetime import time, datetime, date

class User(BaseModel):
    user_fname: str
    # user_lname: str
    # user_gender: str
    # user_phone: int
    # user_email: str
    # user_username: str
    # user_password: str
    # user_address: str
    # id_role: int


class UpdateUser(BaseModel):
    user_fname: str
    user_lname: str
    user_gender: str
    user_phone: str
    user_email: str
    user_username: str
    user_password: str
    user_address: str


class UpdateUserAdmin(BaseModel):
    user_fname: str
    user_lname: str
    user_gender: str
    user_phone: str
    user_email: str
    user_username: str
    user_password: str
    user_address: str
    is_admin: bool


class ShowUser(BaseModel):
    id: Optional[int] = None
    user_username: Optional[str] = None
    user_email: Optional[str] = None
    user_username: Optional[str] = None
    user_phone: Optional[int] = None
    user_gender: Optional[str] = None
    user_fname: Optional[str] = None
    user_lname: Optional[str] = None


class ShowUser(BaseModel):
    id: Optional[int] = None
    user_username: Optional[str] = None
    user_email: Optional[str] = None
    user_username: Optional[str] = None
    user_phone: Optional[int] = None
    user_gender: Optional[str] = None
    user_fname: Optional[str] = None
    user_lname: Optional[str] = None

    class Config:
        from_attributes = True


class Login(BaseModel):
    username: str
    user_pwd: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class SystemFunctions(BaseModel):
    func_name: str
    description: str

    class Config:
        from_attributes = True


class Roles(BaseModel):
    role_name: str
    description: str

    class Config:
        from_attributes = True


class RolesPriviledges(BaseModel):
    func_name: str

    class Config:
        from_attributes = True


class Groups(BaseModel):
    group_name: str
    description: str

    class Config:
        from_attributes = True


class GroupRoles(BaseModel):
    role_name: str


class UserGroup(BaseModel):
    group_name: str


class LineClearance(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class MaterialsReceiving(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class VehiclesInspection(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class MarketingPromotion(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class ReceiptOCR(BaseModel):
    item_description: Dict[str, str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True

