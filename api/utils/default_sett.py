from api import models
from api.database import SessionLocal
import datetime
import json
from api.libs.hashing import Hash
from sqlalchemy.exc import SQLAlchemyError


db = SessionLocal()


def default_admin():
    admin_user = models.User(
        user_username="admin",
        user_email="admin@iconiatech.com",
        user_password=Hash.bcrypt("@MWenendo/..5080"),
        user_status=True,
        user_is_superuser=True,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        created_by="admin",
    )

    user = (
        db.query(models.User)
        .filter(models.User.user_username == admin_user.user_username)
        .first()
    )
    if not user:
        db.add(admin_user)
        db.commit()
    db.close()


def create_system_functions():
    sys_func = open("system_functions.json")
    data = json.load(sys_func)
    for system_functions in data:
        if_sys_func_exist = (
            db.query(models.SystemFunction)
            .filter(models.SystemFunction.func_name == system_functions["func_name"])
            .first()
        )
        if not if_sys_func_exist:
            create_sys_func = models.SystemFunction(
                func_name=system_functions["func_name"],
                description=system_functions["description"],
                is_active=True,
                created_at=f"{datetime.datetime.now()}",
                updated_at=f"{datetime.datetime.now()}",
            )
            db.add(create_sys_func)
            db.commit()
    db.close()


def create_admin_priviledges(id_company, id_user):
    create_access_role = models.Roles(
        role_name="Access Control Role",
        description="Gives user access controll to CRUD opertaions of endpoints",
        id_company=id_company,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(create_access_role)
    db.commit()
    db.close()
    system_func = db.query(models.SystemFunction).all()
    for sys_fun in system_func:
        create_role_priv = models.RolesPriviledges(
            id_role=1,
            id_func=sys_fun.id,
            id_company=id_company,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        db.add(create_role_priv)
        db.commit()
    db.close()

    create_admin_group = models.Groups(
        group_name="Admin Group",
        description="Gives user access control to CRUD opertaions of endpoints",
        id_company=id_company,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(create_admin_group)
    db.commit()
    db.close()

    create_grp_role = models.GroupRoles(
        id_group=1,
        id_role=1,
        id_company=id_company,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.add(create_grp_role)
    db.commit()
    db.close()

    try:
        create_grp_usr = models.GroupUser(
            id_group=1, id_user=id_user, id_company=id_company
        )
        db.add(create_grp_usr)
        db.commit()
        db.close()
    except SQLAlchemyError as e:
        print(e)
