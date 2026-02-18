from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Time,
    BigInteger,
    DateTime,
    Float,
    Date,
)
from api.database import Base

"""

    Models for the intergrations_iconia database tables.

"""

table_args = {"schema": "intergrations_iconia"}

main_table_args = {"schema": "cb_jipange_data"}

class User(Base):
    __table_args__ = table_args
    __tablename__ = "eusers"

    id = Column(Integer, primary_key=True, index=True)
    user_fname = Column(String)
    user_lname = Column(String)
    user_fullname = Column(String)
    user_gender = Column(String)
    user_phone = Column(BigInteger)
    user_email = Column(String, unique=True)
    user_username = Column(String, unique=True)
    user_password = Column(String)
    user_address = Column(String)
    user_joindate = Column(String)
    user_status = Column(Boolean)
    user_is_superuser = Column(Boolean)
    id_role = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    created_by = Column(String)
    id_company = Column(Integer)
    is_admin = Column(Boolean)


class SystemFunction(Base):
    __table_args__ = table_args
    __tablename__ = "esystem_function"

    id = Column(Integer, primary_key=True, index=True)
    func_name = Column(String, unique=True)
    description = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class Roles(Base):
    __table_args__ = table_args
    __tablename__ = "eroles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)
    description = Column(String)
    id_company = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class RolesPriviledges(Base):
    __table_args__ = table_args
    __tablename__ = "eroles_priviledges"

    id = Column(Integer, primary_key=True, index=True)
    id_role = Column(Integer)
    id_func = Column(Integer)
    id_company = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class GroupRoles(Base):
    __table_args__ = table_args
    __tablename__ = "egroups_roles"

    id = Column(Integer, primary_key=True, index=True)
    id_role = Column(Integer)
    id_group = Column(Integer)
    id_company = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class Groups(Base):
    __table_args__ = table_args
    __tablename__ = "egroups"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String)
    description = Column(String)
    id_company = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


class GroupUser(Base):
    __table_args__ = table_args
    __tablename__ = "egroup_user"

    id = Column(Integer, primary_key=True, index=True)
    id_group = Column(BigInteger)
    id_user = Column(Integer)
    id_company = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))


"""

    Models for the compliance tool database tables.

"""

table_args1 = {"schema": "cb_jipange_data"}


class Instance(Base):
    __table_args__ = table_args1
    __tablename__ = "einstances"

    id = Column(BigInteger, primary_key=True, index=True)
    post_date = Column(DateTime(timezone=True))
    modified = Column(DateTime(timezone=True))
    user_id = Column(BigInteger)
    digitization_status = Column(String)
    instance_created_date = Column(String)
    instance_declined_date = Column(String)
    instance_decline_reasons = Column(String)
    completed_source = Column(BigInteger)
    orgstructure_id = Column(BigInteger)
    form_id = Column(BigInteger)
    digitization_type = Column(String)
    instance_name = Column(String)
    instance_completed_date = Column(String)
    non_conformity_status = Column(BigInteger)
    instance_approval_message = Column(String)
    instance_notes = Column(String)
    workflow_assigned_id = Column(BigInteger)
    instance_authorize_notes = Column(String)
    instance_authorize_date = Column(String)
    instance_approval_date = Column(String)
    instance_defer_date = Column(String)
    instance_defer_message = Column(String)
    archive_status = Column(BigInteger)
    instance_submit_date = Column(BigInteger)
    approvals_id = Column(BigInteger)
    approval = Column(String)
    team_id = Column(BigInteger)
    approvals_log_id = Column(BigInteger)
    nc_status = Column(String)
    nc_original_instance_id = Column(BigInteger)
    is_private = Column(Boolean)
    is_workflow = Column(Boolean)
    workflow_id = Column(BigInteger)
    instance_id_from = Column(BigInteger)
    workflow_log_id = Column(BigInteger)
    can_notify = Column(Integer)


class FormLogs(Base):
    __table_args__ = table_args1
    __tablename__ = "eforms_field_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    modified = Column(DateTime(timezone=True))
    post_date = Column(DateTime(timezone=True))
    completed_source = Column(BigInteger)
    user_id = Column(BigInteger)
    instance_id = Column(BigInteger)
    form_item_id = Column(BigInteger)
    form_item_feedback_type = Column(String)
    form_item_feedback_value = Column(String)
    choice_details_id = Column(BigInteger)
    choice_details_ids = Column(String)
    orgstructure_id = Column(BigInteger)


# class FormRowsLogs(Base):
#     __table_args__ = table_args1
#     __tablename__ = "eforms_row_logs"

#     id = Column(BigInteger, primary_key=True, index=True)
#     completed_source = Column(BigInteger)
#     instance_id = Column(BigInteger)
#     orgstructure_id = Column(BigInteger)
#     child_form_id = Column(BigInteger)
#     user_id = Column(BigInteger)
#     row_number = Column(BigInteger)
#     modified = Column(DateTime(timezone=True))
#     post_date = Column(DateTime(timezone=True))
#     row_archive = Column(BigInteger)
#     updated = Column(BigInteger)
#     kpi_count = Column(BigInteger)
#     kpi_breaches = Column(BigInteger)
#     q_one = Column(String)
#     q_two = Column(String)
#     q_three = Column(String)
#     q_four = Column(String)
#     q_five = Column(String)
#     q_six = Column(String)
#     q_seven = Column(String)
#     q_eight = Column(String)
#     q_nine = Column(String)
#     q_ten = Column(String)
#     q_eleven = Column(String)
#     q_twelve = Column(String)
#     q_thirteen = Column(String)
#     q_fourteen = Column(String)
#     q_fifteen = Column(String)
#     q_sixteen = Column(String)
#     q_seventeen = Column(String)
#     q_eighteen = Column(String)
#     q_nineteen = Column(String)
#     q_twenty = Column(String)
#     q_twentyone = Column(String)
#     q_twentytwo = Column(String)
#     q_twentythree = Column(String)
#     q_twentyfour = Column(String)
#     q_twentyfive = Column(String)
#     q_twentysix = Column(String)
#     q_twentyseven = Column(String)
#     q_twentyeight = Column(String)
#     q_twentynine = Column(String)
#     q_thirty = Column(String)
#     nc_prev_child_form_id = Column(BigInteger)


class ChoiceDetails(Base):
    __table_args__ = main_table_args
    __tablename__ = "echoice_details"

    id = Column(BigInteger, primary_key=True, index=True)
    choice_id = Column(BigInteger)
    choice_item = Column(String)
    choice_details_status = Column(String)
    choice_item_no = Column(BigInteger)
    orgstructure_id = Column(BigInteger)
    post_date = Column(DateTime(timezone=True))
    modified = Column(DateTime(timezone=True))
    
class FormRowsLogs(Base):
    __table_args__ = main_table_args
    __tablename__ = "eforms_row_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    completed_source = Column(BigInteger)
    instance_id = Column(BigInteger)
    orgstructure_id = Column(BigInteger)
    child_form_id = Column(BigInteger)
    user_id = Column(BigInteger)
    row_number = Column(BigInteger)
    modified = Column(DateTime(timezone=True))
    post_date = Column(DateTime(timezone=True))
    row_archive = Column(BigInteger)
    updated = Column(BigInteger)
    kpi_count = Column(BigInteger)
    kpi_breaches = Column(BigInteger)
    q_one = Column(String)
    q_two = Column(String)
    q_three = Column(String)
    q_four = Column(String)
    q_five = Column(String)
    q_six = Column(String)
    q_seven = Column(String)
    q_eight = Column(String)
    q_nine = Column(String)
    q_ten = Column(String)
    q_eleven = Column(String)
    q_twelve = Column(String)
    q_thirteen = Column(String)
    q_fourteen = Column(String)
    q_fifteen = Column(String)
    q_sixteen = Column(String)
    q_seventeen = Column(String)
    q_eighteen = Column(String)
    q_nineteen = Column(String)
    q_twenty = Column(String)
    q_twentyone = Column(String)
    q_twentytwo = Column(String)
    q_twentythree = Column(String)
    q_twentyfour = Column(String)
    q_twentyfive = Column(String)
    q_twentysix = Column(String)
    q_twentyseven = Column(String)
    q_twentyeight = Column(String)
    q_twentynine = Column(String)
    q_thirty = Column(String)
    nc_prev_child_form_id = Column(BigInteger)
    is_active = Column(Boolean, default=True)