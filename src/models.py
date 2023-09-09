from typing import Literal


from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from src.database import Base

ROLES = ("admin", "manager", "employee")
Role = Literal[*ROLES]


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    organisations = relationship("Organisation", secondary="user_organisations")
    hashed_password = Column(String)


class UserOrganisation(Base):
    __tablename__ = "user_organisations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    role = Column(String, default="employee")

    __table_args__ = (CheckConstraint(role.in_(ROLES), name="role_check"),)
