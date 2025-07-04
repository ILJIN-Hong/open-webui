from typing import Optional

from open_webui.models.rfq import (
    RFQForm,
    RFQModel,
    RFQUserResponse,
    RFQs,
)
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status

from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access, has_permission

router = APIRouter()

###########################
# Get RFQ List
###########################

@router.get("/list", response_model=list[RFQUserResponse])
async def get_rfqs(user=Depends(get_verified_user)):
    if user.role == "admin":
        return RFQs.get_rfqs()
    else:
        return RFQs.get_rfqs_by_user_id(user.id)

###########################
# Get RFQ by ID
###########################

@router.get("/get/{id}", response_model=Optional[RFQUserResponse])
async def get_rfq_by_id(id: str, user=Depends(get_verified_user)):
    rfq = RFQs.get_rfq_by_id(id)
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        rfq.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "read", rfq.access_control)
    ):
        return rfq
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

###########################
# Create RFQ
###########################

@router.post("/add", response_model=Optional[RFQUserResponse])
async def create_rfq(
    form_data: RFQForm,
    user=Depends(get_verified_user),
):
    rfq = RFQs.insert_new_rfq(form_data, user.id)
    return rfq

###########################
# Update RFQ
###########################

@router.put("/update/{id}", response_model=Optional[RFQUserResponse])
async def update_rfq(
    id: str,
    form_data: RFQForm,
    user=Depends(get_verified_user),
):
    rfq = RFQs.get_rfq_by_id(id)
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        rfq.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "write", rfq.access_control)
    ):
        updated_rfq = RFQs.update_rfq_by_id(id, form_data)
        return updated_rfq
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

###########################
# Delete RFQ
###########################

@router.delete("/delete/{id}")
async def delete_rfq(
    id: str,
    user=Depends(get_verified_user),
):
    rfq = RFQs.get_rfq_by_id(id)
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        rfq.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "write", rfq.access_control)
    ):
        RFQs.delete_rfq_by_id(id)
        return {"message": "RFQ deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        ) 