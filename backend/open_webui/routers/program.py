from typing import Optional

from open_webui.models.program import (
    ProgramForm,
    ProgramModel,
    ProgramUserResponse,
    Programs,
)
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status

from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access, has_permission

router = APIRouter()

###########################
# Get Programs
###########################

@router.get("/", response_model=list[ProgramUserResponse])
async def get_programs(user=Depends(get_verified_user)):
    if user.role == "admin":
        return Programs.get_programs()
    else:
        return Programs.get_programs_by_user_id(user.id)

###########################
# Get Program by ID
###########################

@router.get("/{id}", response_model=Optional[ProgramUserResponse])
async def get_program_by_id(id: str, user=Depends(get_verified_user)):
    program = Programs.get_program_by_id(id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        program.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "read", program.access_control)
    ):
        return program
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

###########################
# Create Program
###########################

@router.post("/", response_model=Optional[ProgramUserResponse])
async def create_program(
    form_data: ProgramForm,
    user=Depends(get_verified_user),
):
    program = Programs.insert_new_program(form_data, user.id)
    return program

###########################
# Update Program
###########################

@router.put("/{id}", response_model=Optional[ProgramUserResponse])
async def update_program(
    id: str,
    form_data: ProgramForm,
    user=Depends(get_verified_user),
):
    program = Programs.get_program_by_id(id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        program.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "write", program.access_control)
    ):
        updated_program = Programs.update_program_by_id(id, form_data)
        return updated_program
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

###########################
# Delete Program
###########################

@router.delete("/{id}")
async def delete_program(
    id: str,
    user=Depends(get_verified_user),
):
    program = Programs.get_program_by_id(id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
    
    if (
        program.user_id == user.id
        or user.role == "admin"
        or has_access(user.id, "write", program.access_control)
    ):
        Programs.delete_program_by_id(id)
        return {"message": "Program deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        ) 