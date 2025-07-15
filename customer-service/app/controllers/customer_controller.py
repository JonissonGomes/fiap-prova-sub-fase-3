from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
import logging

from app.domain.customer import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerSearchRequest, CustomerStatsResponse
)
from app.services.customer_service import CustomerService
from app.middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])

# Dependency para obter o serviço de clientes
async def get_customer_service() -> CustomerService:
    # Esta função será substituída pela dependency no main.py
    pass

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Cria um novo cliente."""
    try:
        customer = await customer_service.create_customer(customer_data)
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna todos os clientes com paginação."""
    try:
        customers = await customer_service.get_all_customers(skip, limit)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    q: Optional[str] = Query(None, description="Busca genérica em nome, CPF, email ou telefone"),
    cpf: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca clientes com base nos critérios fornecidos."""
    try:
        # Se 'q' foi fornecido, buscar em todos os campos
        if q:
            search_request = CustomerSearchRequest(
                cpf=q,
                email=q,
                phone=q,
                name=q
            )
        else:
            # Usar parâmetros específicos
            search_request = CustomerSearchRequest(
                cpf=cpf,
                email=email,
                phone=phone,
                name=name
            )
        
        customers = await customer_service.search_customers(search_request)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/stats", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna estatísticas dos clientes."""
    try:
        stats = await customer_service.get_customer_stats()
        return CustomerStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por ID."""
    try:
        customer = await customer_service.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Atualiza um cliente."""
    try:
        customer = await customer_service.update_customer(customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Remove um cliente."""
    try:
        success = await customer_service.delete_customer(customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/activate", response_model=CustomerResponse)
async def activate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Ativa um cliente."""
    try:
        customer = await customer_service.activate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Desativa um cliente."""
    try:
        customer = await customer_service.deactivate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/cpf/{cpf}", response_model=CustomerResponse)
async def get_customer_by_cpf(
    cpf: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por CPF."""
    try:
        customer = await customer_service.get_customer_by_cpf(cpf)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por CPF: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/email/{email}", response_model=CustomerResponse)
async def get_customer_by_email(
    email: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por email."""
    try:
        customer = await customer_service.get_customer_by_email(email)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por email: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import List, Optional
import logging

from app.domain.customer import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerSearchRequest, CustomerStatsResponse
)
from app.services.customer_service import CustomerService
from app.middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])

# Dependency para obter o serviço de clientes
async def get_customer_service() -> CustomerService:
    # Esta função será substituída pela dependency no main.py
    pass

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Cria um novo cliente."""
    try:
        customer = await customer_service.create_customer(customer_data)
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna todos os clientes com paginação."""
    try:
        customers = await customer_service.get_all_customers(skip, limit)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    q: Optional[str] = Query(None, description="Busca genérica em nome, CPF, email ou telefone"),
    cpf: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca clientes com base nos critérios fornecidos."""
    try:
        # Se 'q' foi fornecido, buscar em todos os campos
        if q:
            search_request = CustomerSearchRequest(
                cpf=q,
                email=q,
                phone=q,
                name=q
            )
        else:
            # Usar parâmetros específicos
            search_request = CustomerSearchRequest(
                cpf=cpf,
                email=email,
                phone=phone,
                name=name
            )
        
        customers = await customer_service.search_customers(search_request)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/stats", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna estatísticas dos clientes."""
    try:
        stats = await customer_service.get_customer_stats()
        return CustomerStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por ID."""
    try:
        customer = await customer_service.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Atualiza um cliente."""
    try:
        customer = await customer_service.update_customer(customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Remove um cliente."""
    try:
        success = await customer_service.delete_customer(customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/activate", response_model=CustomerResponse)
async def activate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Ativa um cliente."""
    try:
        customer = await customer_service.activate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Desativa um cliente."""
    try:
        customer = await customer_service.deactivate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/cpf/{cpf}", response_model=CustomerResponse)
async def get_customer_by_cpf(
    cpf: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por CPF."""
    try:
        customer = await customer_service.get_customer_by_cpf(cpf)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por CPF: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/email/{email}", response_model=CustomerResponse)
async def get_customer_by_email(
    email: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por email."""
    try:
        customer = await customer_service.get_customer_by_email(email)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por email: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import List, Optional
import logging

from app.domain.customer import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerSearchRequest, CustomerStatsResponse
)
from app.services.customer_service import CustomerService
from app.middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])

# Dependency para obter o serviço de clientes
async def get_customer_service() -> CustomerService:
    # Esta função será substituída pela dependency no main.py
    pass

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Cria um novo cliente."""
    try:
        customer = await customer_service.create_customer(customer_data)
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna todos os clientes com paginação."""
    try:
        customers = await customer_service.get_all_customers(skip, limit)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    q: Optional[str] = Query(None, description="Busca genérica em nome, CPF, email ou telefone"),
    cpf: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca clientes com base nos critérios fornecidos."""
    try:
        # Se 'q' foi fornecido, buscar em todos os campos
        if q:
            search_request = CustomerSearchRequest(
                cpf=q,
                email=q,
                phone=q,
                name=q
            )
        else:
            # Usar parâmetros específicos
            search_request = CustomerSearchRequest(
                cpf=cpf,
                email=email,
                phone=phone,
                name=name
            )
        
        customers = await customer_service.search_customers(search_request)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/stats", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna estatísticas dos clientes."""
    try:
        stats = await customer_service.get_customer_stats()
        return CustomerStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por ID."""
    try:
        customer = await customer_service.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Atualiza um cliente."""
    try:
        customer = await customer_service.update_customer(customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Remove um cliente."""
    try:
        success = await customer_service.delete_customer(customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/activate", response_model=CustomerResponse)
async def activate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Ativa um cliente."""
    try:
        customer = await customer_service.activate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Desativa um cliente."""
    try:
        customer = await customer_service.deactivate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/cpf/{cpf}", response_model=CustomerResponse)
async def get_customer_by_cpf(
    cpf: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por CPF."""
    try:
        customer = await customer_service.get_customer_by_cpf(cpf)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por CPF: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/email/{email}", response_model=CustomerResponse)
async def get_customer_by_email(
    email: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por email."""
    try:
        customer = await customer_service.get_customer_by_email(email)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por email: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import List, Optional
import logging

from app.domain.customer import (
    Customer, CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerSearchRequest, CustomerStatsResponse
)
from app.services.customer_service import CustomerService
from app.middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])

# Dependency para obter o serviço de clientes
async def get_customer_service() -> CustomerService:
    # Esta função será substituída pela dependency no main.py
    pass

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Cria um novo cliente."""
    try:
        customer = await customer_service.create_customer(customer_data)
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna todos os clientes com paginação."""
    try:
        customers = await customer_service.get_all_customers(skip, limit)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    q: Optional[str] = Query(None, description="Busca genérica em nome, CPF, email ou telefone"),
    cpf: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca clientes com base nos critérios fornecidos."""
    try:
        # Se 'q' foi fornecido, buscar em todos os campos
        if q:
            search_request = CustomerSearchRequest(
                cpf=q,
                email=q,
                phone=q,
                name=q
            )
        else:
            # Usar parâmetros específicos
            search_request = CustomerSearchRequest(
                cpf=cpf,
                email=email,
                phone=phone,
                name=name
            )
        
        customers = await customer_service.search_customers(search_request)
        return [CustomerResponse(**customer.dict()) for customer in customers]
    except Exception as e:
        logger.error(f"Erro ao buscar clientes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/stats", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Retorna estatísticas dos clientes."""
    try:
        stats = await customer_service.get_customer_stats()
        return CustomerStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por ID."""
    try:
        customer = await customer_service.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Atualiza um cliente."""
    try:
        customer = await customer_service.update_customer(customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Remove um cliente."""
    try:
        success = await customer_service.delete_customer(customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/activate", response_model=CustomerResponse)
async def activate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Ativa um cliente."""
    try:
        customer = await customer_service.activate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{customer_id}/deactivate", response_model=CustomerResponse)
async def deactivate_customer(
    customer_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Desativa um cliente."""
    try:
        customer = await customer_service.deactivate_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desativar cliente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/cpf/{cpf}", response_model=CustomerResponse)
async def get_customer_by_cpf(
    cpf: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por CPF."""
    try:
        customer = await customer_service.get_customer_by_cpf(cpf)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por CPF: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/email/{email}", response_model=CustomerResponse)
async def get_customer_by_email(
    email: str,
    current_user: dict = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Busca um cliente por email."""
    try:
        customer = await customer_service.get_customer_by_email(email)
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return CustomerResponse(**customer.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por email: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 