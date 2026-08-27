from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from ..schemas import OperationResponse, CreateOperation
from ..db.config import get_db
from ..services import OperationService, ReceiptService

class OperationRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/operations")
        self.router.add_api_route("/", self.get_operations, response_model=List[OperationResponse], methods=["GET"])
        self.router.add_api_route("/{id}", self.get_operation, response_model=OperationResponse, methods=["GET"])
        self.router.add_api_route("/new", self.create_operation, response_model=OperationResponse, methods=["POST"])
        self.router.add_api_route("/from-receipt", self.create_operation_from_receipt, response_model=OperationResponse, methods=["POST"])

    @staticmethod
    def get_operations(request: Request, db: Session = Depends(get_db)):
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        operation_services = OperationService(db)
        operations = operation_services.get_by_user(user['id'])
        return operations
    
    @staticmethod
    def get_operation(id: int, request: Request, db: Session = Depends(get_db)):
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        operation_services = OperationService(db)
        operation = operation_services.get_by_user_and_id(user['id'], id)
        return operation
    
    @staticmethod
    def create_operation(operation: CreateOperation, request: Request, db: Session = Depends(get_db)):
        print({'operation_from_form_in_routes': operation.to_dict})
        user= request.state.user
        print("--------------------REQUEST.STATE.USER-----------------")
        print(user)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        operation_services = OperationService(db)
        new_operation = operation_services.create_new(user['id'], operation)
        print(f"New operation with concept '{operation.concept}' was created successfully")
        return new_operation

    @staticmethod
    async def create_operation_from_receipt(
        request: Request,
        file: UploadFile = File(...),
        account_id: int = Form(...),
        db: Session = Depends(get_db),
    ):
        """Create an operation automatically from an uploaded receipt (PDF/image):
        the text is extracted server-side and structured by the AI provider."""
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        file_bytes = await file.read()
        print(f"Receipt '{file.filename}' ({len(file_bytes)} bytes) for account {account_id}")
        receipt_service = ReceiptService(db)
        new_operation = receipt_service.create_from_receipt(user['id'], file_bytes, file.filename, account_id)
        print(f"Operation from receipt '{file.filename}' was created successfully")
        return new_operation