import json
import time
import uuid
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.utils.access_control import has_access
from open_webui.models.users import Users, UserResponse

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, JSON
from sqlalchemy import or_, func, select, and_, text
from sqlalchemy.sql import exists

####################
# Program DB Schema
####################

class Program(Base):
    __tablename__ = "program"

    id = Column(Text, primary_key=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text, nullable=True)
    status = Column(Text, default="active")  # active, inactive
    properties = Column(JSON, nullable=True)  # 트리 구조 데이터
    summary_format = Column(JSON, nullable=True)  # 요약 포맷
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

    access_control = Column(JSON, nullable=True)

class ProgramModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    name: str
    description: Optional[str] = None
    status: str = "active"
    properties: Optional[dict] = None
    summary_format: Optional[dict] = None
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    access_control: Optional[dict] = None

####################
# Forms
####################

class ProgramForm(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    properties: Optional[dict] = None
    summary_format: Optional[dict] = None
    access_control: Optional[dict] = None

class ProgramUserResponse(ProgramModel):
    user: Optional[UserResponse] = None

class ProgramTable:
    def insert_new_program(
        self,
        form_data: ProgramForm,
        user_id: str,
    ) -> Optional[ProgramModel]:
        with get_db() as db:
            program = ProgramModel(
                **{
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    **form_data.model_dump(),
                    "created_at": int(time.time_ns()),
                    "updated_at": int(time.time_ns()),
                }
            )

            new_program = Program(**program.model_dump())

            db.add(new_program)
            db.commit()
            return program

    def get_programs(self) -> list[ProgramModel]:
        with get_db() as db:
            programs = db.query(Program).order_by(Program.updated_at.desc()).all()
            return [ProgramModel.model_validate(program) for program in programs]

    def get_programs_by_user_id(
        self, user_id: str, permission: str = "write"
    ) -> list[ProgramModel]:
        programs = self.get_programs()
        return [
            program
            for program in programs
            if program.user_id == user_id
            or has_access(user_id, permission, program.access_control)
        ]

    def get_program_by_id(self, id: str) -> Optional[ProgramModel]:
        with get_db() as db:
            program = db.query(Program).filter(Program.id == id).first()
            return ProgramModel.model_validate(program) if program else None

    def update_program_by_id(self, id: str, form_data: ProgramForm) -> Optional[ProgramModel]:
        with get_db() as db:
            program = db.query(Program).filter(Program.id == id).first()
            if not program:
                return None

            program.name = form_data.name
            program.description = form_data.description
            program.status = form_data.status
            program.properties = form_data.properties
            program.summary_format = form_data.summary_format
            program.access_control = form_data.access_control
            program.updated_at = int(time.time_ns())

            db.commit()
            return ProgramModel.model_validate(program) if program else None

    def delete_program_by_id(self, id: str):
        with get_db() as db:
            db.query(Program).filter(Program.id == id).delete()
            db.commit()
            return True

Programs = ProgramTable() 