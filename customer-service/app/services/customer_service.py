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
        """Busca todos os clientes com paginação."""
        return await self.repository.get_all(skip, limit)

    async def update_customer(self, customer_id: str, customer_data: CustomerUpdate) -> Optional[Customer]:
        """Atualiza um cliente."""
        # Busca o cliente existente
        existing_customer = await self.repository.get_by_id(customer_id)
        if not existing_customer:
            return None
        
        # Verifica se o email está sendo alterado e se já existe outro cliente com o mesmo email
        if customer_data.email and customer_data.email != existing_customer.email:
            email_customer = await self.repository.get_by_email(customer_data.email)
            if email_customer and email_customer.id != customer_id:
                raise ValueError("Já existe um cliente com este email")
        
        # Atualiza os dados
        update_data = customer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_customer, field, value)
        
        existing_customer.updated_at = datetime.utcnow()
        
        return await self.repository.update(existing_customer)

    async def delete_customer(self, customer_id: str) -> bool:
        """Deleta um cliente (soft delete)."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            return False
        
        customer.active = False
        customer.updated_at = datetime.utcnow()
        
        await self.repository.update(customer)
        return True

    async def get_customer_stats(self) -> CustomerStatsResponse:
        """Obtém estatísticas dos clientes."""
        return await self.repository.get_stats() 