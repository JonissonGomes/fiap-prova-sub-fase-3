from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.domain.customer import Customer, CustomerCreate, CustomerUpdate, CustomerSearchRequest, CustomerStatsResponse
from app.adapters.mongodb_customer_repository import MongoDBCustomerRepository

class CustomerService:
    def __init__(self, repository: MongoDBCustomerRepository):
        self.repository = repository

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Cria um novo cliente."""
        # Verifica se já existe um cliente com o mesmo CPF
        existing_customer = await self.repository.get_by_cpf(customer_data.cpf)
        if existing_customer:
            raise ValueError("Já existe um cliente com este CPF")
        
        # Verifica se já existe um cliente com o mesmo email
        existing_customer = await self.repository.get_by_email(customer_data.email)
        if existing_customer:
            raise ValueError("Já existe um cliente com este email")
        
        # Cria o cliente
        customer = Customer(
            **customer_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.repository.create(customer)

    async def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        return await self.repository.get_by_id(customer_id)

    async def get_customer_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        return await self.repository.get_by_cpf(cpf)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        return await self.repository.get_by_email(email)

    async def search_customers(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        return await self.repository.search(search_request)

    async def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        return await self.repository.get_all(skip, limit)

    async def update_customer(self, customer_id: str, customer_update: CustomerUpdate) -> Optional[Customer]:
        """Atualiza um cliente."""
        # Verifica se o cliente existe
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None
        
        # Se está atualizando o email, verifica se já existe outro cliente com o mesmo email
        if customer_update.email and customer_update.email != existing_customer.email:
            email_customer = await self.repository.get_by_email(customer_update.email)
            if email_customer and email_customer.id != customer_id:
                raise ValueError("Já existe um cliente com este email")
        
        # Atualiza o cliente
        update_data = customer_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        return await self.repository.update(customer_id, update_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        return await self.repository.delete(customer_id)

    async def activate_customer(self, customer_id: str) -> Optional[Customer]:
        """Ativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': True,
            'updated_at': datetime.utcnow()
        })

    async def deactivate_customer(self, customer_id: str) -> Optional[Customer]:
        """Desativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': False,
            'updated_at': datetime.utcnow()
        })

    async def get_customer_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        return await self.repository.get_stats() 
from datetime import datetime
from bson import ObjectId

from app.domain.customer import Customer, CustomerCreate, CustomerUpdate, CustomerSearchRequest, CustomerStatsResponse
from app.adapters.mongodb_customer_repository import MongoDBCustomerRepository

class CustomerService:
    def __init__(self, repository: MongoDBCustomerRepository):
        self.repository = repository

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Cria um novo cliente."""
        # Verifica se já existe um cliente com o mesmo CPF
        existing_customer = await self.repository.get_by_cpf(customer_data.cpf)
        if existing_customer:
            raise ValueError("Já existe um cliente com este CPF")
        
        # Verifica se já existe um cliente com o mesmo email
        existing_customer = await self.repository.get_by_email(customer_data.email)
        if existing_customer:
            raise ValueError("Já existe um cliente com este email")
        
        # Cria o cliente
        customer = Customer(
            **customer_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.repository.create(customer)

    async def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        return await self.repository.get_by_id(customer_id)

    async def get_customer_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        return await self.repository.get_by_cpf(cpf)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        return await self.repository.get_by_email(email)

    async def search_customers(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        return await self.repository.search(search_request)

    async def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        return await self.repository.get_all(skip, limit)

    async def update_customer(self, customer_id: str, customer_update: CustomerUpdate) -> Optional[Customer]:
        """Atualiza um cliente."""
        # Verifica se o cliente existe
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None
        
        # Se está atualizando o email, verifica se já existe outro cliente com o mesmo email
        if customer_update.email and customer_update.email != existing_customer.email:
            email_customer = await self.repository.get_by_email(customer_update.email)
            if email_customer and email_customer.id != customer_id:
                raise ValueError("Já existe um cliente com este email")
        
        # Atualiza o cliente
        update_data = customer_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        return await self.repository.update(customer_id, update_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        return await self.repository.delete(customer_id)

    async def activate_customer(self, customer_id: str) -> Optional[Customer]:
        """Ativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': True,
            'updated_at': datetime.utcnow()
        })

    async def deactivate_customer(self, customer_id: str) -> Optional[Customer]:
        """Desativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': False,
            'updated_at': datetime.utcnow()
        })

    async def get_customer_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        return await self.repository.get_stats() 
from datetime import datetime
from bson import ObjectId

from app.domain.customer import Customer, CustomerCreate, CustomerUpdate, CustomerSearchRequest, CustomerStatsResponse
from app.adapters.mongodb_customer_repository import MongoDBCustomerRepository

class CustomerService:
    def __init__(self, repository: MongoDBCustomerRepository):
        self.repository = repository

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Cria um novo cliente."""
        # Verifica se já existe um cliente com o mesmo CPF
        existing_customer = await self.repository.get_by_cpf(customer_data.cpf)
        if existing_customer:
            raise ValueError("Já existe um cliente com este CPF")
        
        # Verifica se já existe um cliente com o mesmo email
        existing_customer = await self.repository.get_by_email(customer_data.email)
        if existing_customer:
            raise ValueError("Já existe um cliente com este email")
        
        # Cria o cliente
        customer = Customer(
            **customer_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.repository.create(customer)

    async def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        return await self.repository.get_by_id(customer_id)

    async def get_customer_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        return await self.repository.get_by_cpf(cpf)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        return await self.repository.get_by_email(email)

    async def search_customers(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        return await self.repository.search(search_request)

    async def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        return await self.repository.get_all(skip, limit)

    async def update_customer(self, customer_id: str, customer_update: CustomerUpdate) -> Optional[Customer]:
        """Atualiza um cliente."""
        # Verifica se o cliente existe
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None
        
        # Se está atualizando o email, verifica se já existe outro cliente com o mesmo email
        if customer_update.email and customer_update.email != existing_customer.email:
            email_customer = await self.repository.get_by_email(customer_update.email)
            if email_customer and email_customer.id != customer_id:
                raise ValueError("Já existe um cliente com este email")
        
        # Atualiza o cliente
        update_data = customer_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        return await self.repository.update(customer_id, update_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        return await self.repository.delete(customer_id)

    async def activate_customer(self, customer_id: str) -> Optional[Customer]:
        """Ativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': True,
            'updated_at': datetime.utcnow()
        })

    async def deactivate_customer(self, customer_id: str) -> Optional[Customer]:
        """Desativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': False,
            'updated_at': datetime.utcnow()
        })

    async def get_customer_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        return await self.repository.get_stats() 
from datetime import datetime
from bson import ObjectId

from app.domain.customer import Customer, CustomerCreate, CustomerUpdate, CustomerSearchRequest, CustomerStatsResponse
from app.adapters.mongodb_customer_repository import MongoDBCustomerRepository

class CustomerService:
    def __init__(self, repository: MongoDBCustomerRepository):
        self.repository = repository

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Cria um novo cliente."""
        # Verifica se já existe um cliente com o mesmo CPF
        existing_customer = await self.repository.get_by_cpf(customer_data.cpf)
        if existing_customer:
            raise ValueError("Já existe um cliente com este CPF")
        
        # Verifica se já existe um cliente com o mesmo email
        existing_customer = await self.repository.get_by_email(customer_data.email)
        if existing_customer:
            raise ValueError("Já existe um cliente com este email")
        
        # Cria o cliente
        customer = Customer(
            **customer_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.repository.create(customer)

    async def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        return await self.repository.get_by_id(customer_id)

    async def get_customer_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        return await self.repository.get_by_cpf(cpf)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        return await self.repository.get_by_email(email)

    async def search_customers(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        return await self.repository.search(search_request)

    async def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        return await self.repository.get_all(skip, limit)

    async def update_customer(self, customer_id: str, customer_update: CustomerUpdate) -> Optional[Customer]:
        """Atualiza um cliente."""
        # Verifica se o cliente existe
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None
        
        # Se está atualizando o email, verifica se já existe outro cliente com o mesmo email
        if customer_update.email and customer_update.email != existing_customer.email:
            email_customer = await self.repository.get_by_email(customer_update.email)
            if email_customer and email_customer.id != customer_id:
                raise ValueError("Já existe um cliente com este email")
        
        # Atualiza o cliente
        update_data = customer_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        return await self.repository.update(customer_id, update_data)

    async def delete_customer(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        return await self.repository.delete(customer_id)

    async def activate_customer(self, customer_id: str) -> Optional[Customer]:
        """Ativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': True,
            'updated_at': datetime.utcnow()
        })

    async def deactivate_customer(self, customer_id: str) -> Optional[Customer]:
        """Desativa um cliente."""
        return await self.repository.update(customer_id, {
            'active': False,
            'updated_at': datetime.utcnow()
        })

    async def get_customer_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        return await self.repository.get_stats() 