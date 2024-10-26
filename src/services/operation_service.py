from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ..core import Security
from ..models import Operation, OperationType
from ..schemas import CreateOperation

class OperationService():
    def __init__(self, db: Session):
        self.db = db
        self.security= Security()

    def get_by_user(self, user_id: int):
        operations = self.db.query(Operation).filter(Operation.user_id == user_id).all()
        operations_dict = [operation.__dict__ for operation in operations]
        for operation in operations_dict:
            operation.pop('_sa_instance_state', None)
        return JSONResponse(content=operations_dict, status_code=status.HTTP_200_OK)
    
    def get_by_user_and_id(self, user_id: int, id: int):
        operation = self.db.query(Operation).filter(and_(Operation.user_id == user_id, Operation.id == id)).first()
        operation_dict = operation.__dict__
        operation.pop('_sa_instance_state', None)
        return JSONResponse(content=operation_dict, status_code=status.HTTP_200_OK)
    
    def create_new(self, user_id: int,  operation: CreateOperation):
        print({'operation_from_form_in_service': operation.to_dict})
        if operation.type.lower() == 'egreso':
            operation.type = OperationType.expense
        elif operation.type.lower() == 'ingreso':
            operation.type = OperationType.income
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not valid operation type, you must enter {[member.value for member in OperationType]} or {[member.value.lower() for member in OperationType]}")
        new_operation = Operation(concept=operation.concept, amount=operation.amount, type=operation.type, user_id=operation.user_id)
        print({'new_operation': new_operation})
        self.db.add(new_operation)
        self.db.commit()
        self.db.refresh(new_operation)
        new_operation_dict = new_operation.__dict__.copy()
        print({'new_operation_dict': new_operation_dict})
        new_operation_dict.pop('_sa_instance_state', None)
        new_operation_dict['date'] = '{:%Y-%m-%d %H:%M}'.format(new_operation_dict['date'])
        return JSONResponse(content=new_operation_dict, status_code=status.HTTP_201_CREATED)