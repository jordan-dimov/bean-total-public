from typing import Literal

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base

ROLES = ("admin", "manager", "employee")
Role = Literal[*ROLES]


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)  # noqa: A003
    name = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True)
    organisations = relationship("Organisation", secondary="user_organisations")
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class UserOrganisation(Base):
    __tablename__ = "user_organisations"

    id = Column(Integer, primary_key=True)  # noqa: A003
    user_email = Column(String, ForeignKey("users.email"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    role = Column(String, default="employee")

    __table_args__ = (CheckConstraint(role.in_(ROLES), name="role_check"),)
