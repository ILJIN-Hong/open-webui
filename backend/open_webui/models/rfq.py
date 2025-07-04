import time
import uuid
from typing import Optional
from open_webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Text, BigInteger, JSON

####################
# RFQ DB Schema
####################

class RFQ(Base):
    __tablename__ = "rfq"
    id = Column(Text, primary_key=True)
    user_id = Column(Text)
    title = Column(Text)
    description = Column(Text, nullable=True)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

class RFQModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    created_at: int
    updated_at: int

class RFQForm(BaseModel):
    title: str
    description: Optional[str] = None

class RFQUserResponse(RFQModel):
    pass

class RFQTable:
    def insert_new_rfq(self, form_data: RFQForm, user_id: str) -> Optional[RFQModel]:
        with get_db() as db:
            rfq = RFQModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=form_data.title,
                description=form_data.description,
                created_at=int(time.time()),
                updated_at=int(time.time()),
            )
            new_rfq = RFQ(**rfq.model_dump())
            db.add(new_rfq)
            db.commit()
            return rfq

    def get_rfqs(self) -> list[RFQModel]:
        with get_db() as db:
            rfqs = db.query(RFQ).order_by(RFQ.updated_at.desc()).all()
            return [RFQModel.model_validate(rfq) for rfq in rfqs]

    def get_rfqs_by_user_id(self, user_id: str) -> list[RFQModel]:
        rfqs = self.get_rfqs()
        return [rfq for rfq in rfqs if rfq.user_id == user_id]

    def get_rfq_by_id(self, id: str) -> Optional[RFQModel]:
        with get_db() as db:
            rfq = db.query(RFQ).filter(RFQ.id == id).first()
            return RFQModel.model_validate(rfq) if rfq else None

    def update_rfq_by_id(self, id: str, form_data: RFQForm) -> Optional[RFQModel]:
        with get_db() as db:
            rfq = db.query(RFQ).filter(RFQ.id == id).first()
            if not rfq:
                return None
            rfq.title = form_data.title
            rfq.description = form_data.description
            rfq.updated_at = int(time.time())
            db.commit()
            return RFQModel.model_validate(rfq)

    def delete_rfq_by_id(self, id: str):
        with get_db() as db:
            db.query(RFQ).filter(RFQ.id == id).delete()
            db.commit()
            return True

RFQs = RFQTable() 