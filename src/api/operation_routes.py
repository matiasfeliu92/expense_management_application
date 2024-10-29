from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from ..schemas import OperationResponse, CreateOperation
from ..db.config import get_db
from ..services import OperationService

class OperationRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/operations")
        self.router.add_api_route("/", self.get_operations, response_model=List[OperationResponse], methods=["GET"])
        self.router.add_api_route("/{id}", self.get_operation, response_model=OperationResponse, methods=["GET"])
        self.router.add_api_route("/new", self.create_operation, response_model=OperationResponse, methods=["POST"])

    @staticmethod
    def get_operations(self, request: Request, db: Session = Depends(get_db)):
        user= request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        operation_services = OperationService(db)
        operations = operation_services.get_by_user(user.id)
        return operations
    
    @staticmethod
    def get_operation(self, id: int, request: Request, db: Session = Depends(get_db)):
        user= request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        operation_services = OperationService(db)
        operation = operation_services.get_by_user_and_id(user.id, id)
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