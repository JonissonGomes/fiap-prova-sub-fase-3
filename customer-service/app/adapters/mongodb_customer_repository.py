from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from app.domain.customer import Customer, CustomerSearchRequest, CustomerStatsResponse

logger = logging.getLogger(__name__)

class MongoDBCustomerRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    async def create(self, customer: Customer) -> Customer:
        """Cria um novo cliente no banco de dados."""
        try:
            customer_dict = customer.dict(exclude={"id"})
            result = await self.collection.insert_one(customer_dict)
            customer.id = str(result.inserted_id)
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            raise

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        try:
            doc = await self.collection.find_one({"cpf": cpf})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por email: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar todos os clientes: {e}")
            raise

    async def search(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        try:
            # Verificar se todos os campos têm o mesmo valor (busca genérica)
            search_values = [
                search_request.cpf,
                search_request.email,
                search_request.phone,
                search_request.name
            ]
            
            # Remover valores None
            non_none_values = [v for v in search_values if v is not None]
            
            # Se todos os valores não-None são iguais, fazer busca OR
            if len(set(non_none_values)) == 1 and len(non_none_values) > 1:
                # Busca genérica com OR
                search_term = non_none_values[0]
                query = {
                    "$or": [
                        {"cpf": search_term},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"phone": {"$regex": search_term, "$options": "i"}},
                        {"name": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            else:
                # Busca específica com AND
                query = {}
                
                if search_request.cpf:
                    query["cpf"] = search_request.cpf
                
                if search_request.email:
                    query["email"] = {"$regex": search_request.email, "$options": "i"}
                
                if search_request.phone:
                    query["phone"] = {"$regex": search_request.phone, "$options": "i"}
                
                if search_request.name:
                    query["name"] = {"$regex": search_request.name, "$options": "i"}
            
            # Se nenhum critério foi fornecido, retorna lista vazia
            if not query:
                return []
            
            cursor = self.collection.find(query).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            raise

    async def update(self, customer_id: str, update_data: dict) -> Optional[Customer]:
        """Atualiza um cliente."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return await self.get_by_id(customer_id)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            raise

    async def delete(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {e}")
            raise

    async def get_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        try:
            # Total de clientes
            total_customers = await self.collection.count_documents({})
            
            # Clientes ativos
            active_customers = await self.collection.count_documents({"active": True})
            
            # Clientes inativos
            inactive_customers = total_customers - active_customers
            
            # Clientes cadastrados este mês
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            customers_this_month = await self.collection.count_documents({
                "created_at": {"$gte": start_of_month}
            })
            
            return CustomerStatsResponse(
                total_customers=total_customers,
                active_customers=active_customers,
                inactive_customers=inactive_customers,
                customers_this_month=customers_this_month
            )
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            raise

    async def create_indexes(self):
        """Cria índices para otimizar as consultas."""
        try:
            # Índice único para CPF
            await self.collection.create_index("cpf", unique=True)
            
            # Índice único para email
            await self.collection.create_index("email", unique=True)
            
            # Índice para telefone
            await self.collection.create_index("phone")
            
            # Índice para nome (para busca por texto)
            await self.collection.create_index("name")
            
            # Índice para data de criação
            await self.collection.create_index("created_at")
            
            # Índice para status ativo
            await self.collection.create_index("active")
            
            logger.info("Índices criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise 
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from app.domain.customer import Customer, CustomerSearchRequest, CustomerStatsResponse

logger = logging.getLogger(__name__)

class MongoDBCustomerRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    async def create(self, customer: Customer) -> Customer:
        """Cria um novo cliente no banco de dados."""
        try:
            customer_dict = customer.dict(exclude={"id"})
            result = await self.collection.insert_one(customer_dict)
            customer.id = str(result.inserted_id)
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            raise

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        try:
            doc = await self.collection.find_one({"cpf": cpf})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por email: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar todos os clientes: {e}")
            raise

    async def search(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        try:
            # Verificar se todos os campos têm o mesmo valor (busca genérica)
            search_values = [
                search_request.cpf,
                search_request.email,
                search_request.phone,
                search_request.name
            ]
            
            # Remover valores None
            non_none_values = [v for v in search_values if v is not None]
            
            # Se todos os valores não-None são iguais, fazer busca OR
            if len(set(non_none_values)) == 1 and len(non_none_values) > 1:
                # Busca genérica com OR
                search_term = non_none_values[0]
                query = {
                    "$or": [
                        {"cpf": search_term},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"phone": {"$regex": search_term, "$options": "i"}},
                        {"name": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            else:
                # Busca específica com AND
                query = {}
                
                if search_request.cpf:
                    query["cpf"] = search_request.cpf
                
                if search_request.email:
                    query["email"] = {"$regex": search_request.email, "$options": "i"}
                
                if search_request.phone:
                    query["phone"] = {"$regex": search_request.phone, "$options": "i"}
                
                if search_request.name:
                    query["name"] = {"$regex": search_request.name, "$options": "i"}
            
            # Se nenhum critério foi fornecido, retorna lista vazia
            if not query:
                return []
            
            cursor = self.collection.find(query).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            raise

    async def update(self, customer_id: str, update_data: dict) -> Optional[Customer]:
        """Atualiza um cliente."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return await self.get_by_id(customer_id)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            raise

    async def delete(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {e}")
            raise

    async def get_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        try:
            # Total de clientes
            total_customers = await self.collection.count_documents({})
            
            # Clientes ativos
            active_customers = await self.collection.count_documents({"active": True})
            
            # Clientes inativos
            inactive_customers = total_customers - active_customers
            
            # Clientes cadastrados este mês
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            customers_this_month = await self.collection.count_documents({
                "created_at": {"$gte": start_of_month}
            })
            
            return CustomerStatsResponse(
                total_customers=total_customers,
                active_customers=active_customers,
                inactive_customers=inactive_customers,
                customers_this_month=customers_this_month
            )
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            raise

    async def create_indexes(self):
        """Cria índices para otimizar as consultas."""
        try:
            # Índice único para CPF
            await self.collection.create_index("cpf", unique=True)
            
            # Índice único para email
            await self.collection.create_index("email", unique=True)
            
            # Índice para telefone
            await self.collection.create_index("phone")
            
            # Índice para nome (para busca por texto)
            await self.collection.create_index("name")
            
            # Índice para data de criação
            await self.collection.create_index("created_at")
            
            # Índice para status ativo
            await self.collection.create_index("active")
            
            logger.info("Índices criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise 
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from app.domain.customer import Customer, CustomerSearchRequest, CustomerStatsResponse

logger = logging.getLogger(__name__)

class MongoDBCustomerRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    async def create(self, customer: Customer) -> Customer:
        """Cria um novo cliente no banco de dados."""
        try:
            customer_dict = customer.dict(exclude={"id"})
            result = await self.collection.insert_one(customer_dict)
            customer.id = str(result.inserted_id)
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            raise

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        try:
            doc = await self.collection.find_one({"cpf": cpf})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por email: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar todos os clientes: {e}")
            raise

    async def search(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        try:
            # Verificar se todos os campos têm o mesmo valor (busca genérica)
            search_values = [
                search_request.cpf,
                search_request.email,
                search_request.phone,
                search_request.name
            ]
            
            # Remover valores None
            non_none_values = [v for v in search_values if v is not None]
            
            # Se todos os valores não-None são iguais, fazer busca OR
            if len(set(non_none_values)) == 1 and len(non_none_values) > 1:
                # Busca genérica com OR
                search_term = non_none_values[0]
                query = {
                    "$or": [
                        {"cpf": search_term},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"phone": {"$regex": search_term, "$options": "i"}},
                        {"name": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            else:
                # Busca específica com AND
                query = {}
                
                if search_request.cpf:
                    query["cpf"] = search_request.cpf
                
                if search_request.email:
                    query["email"] = {"$regex": search_request.email, "$options": "i"}
                
                if search_request.phone:
                    query["phone"] = {"$regex": search_request.phone, "$options": "i"}
                
                if search_request.name:
                    query["name"] = {"$regex": search_request.name, "$options": "i"}
            
            # Se nenhum critério foi fornecido, retorna lista vazia
            if not query:
                return []
            
            cursor = self.collection.find(query).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            raise

    async def update(self, customer_id: str, update_data: dict) -> Optional[Customer]:
        """Atualiza um cliente."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return await self.get_by_id(customer_id)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            raise

    async def delete(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {e}")
            raise

    async def get_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        try:
            # Total de clientes
            total_customers = await self.collection.count_documents({})
            
            # Clientes ativos
            active_customers = await self.collection.count_documents({"active": True})
            
            # Clientes inativos
            inactive_customers = total_customers - active_customers
            
            # Clientes cadastrados este mês
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            customers_this_month = await self.collection.count_documents({
                "created_at": {"$gte": start_of_month}
            })
            
            return CustomerStatsResponse(
                total_customers=total_customers,
                active_customers=active_customers,
                inactive_customers=inactive_customers,
                customers_this_month=customers_this_month
            )
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            raise

    async def create_indexes(self):
        """Cria índices para otimizar as consultas."""
        try:
            # Índice único para CPF
            await self.collection.create_index("cpf", unique=True)
            
            # Índice único para email
            await self.collection.create_index("email", unique=True)
            
            # Índice para telefone
            await self.collection.create_index("phone")
            
            # Índice para nome (para busca por texto)
            await self.collection.create_index("name")
            
            # Índice para data de criação
            await self.collection.create_index("created_at")
            
            # Índice para status ativo
            await self.collection.create_index("active")
            
            logger.info("Índices criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise 
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from app.domain.customer import Customer, CustomerSearchRequest, CustomerStatsResponse

logger = logging.getLogger(__name__)

class MongoDBCustomerRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    async def create(self, customer: Customer) -> Customer:
        """Cria um novo cliente no banco de dados."""
        try:
            customer_dict = customer.dict(exclude={"id"})
            result = await self.collection.insert_one(customer_dict)
            customer.id = str(result.inserted_id)
            return customer
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca um cliente por ID."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(customer_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            raise

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Busca um cliente por CPF."""
        try:
            doc = await self.collection.find_one({"cpf": cpf})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Busca um cliente por email."""
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Customer(**doc)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por email: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Retorna todos os clientes com paginação."""
        try:
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar todos os clientes: {e}")
            raise

    async def search(self, search_request: CustomerSearchRequest) -> List[Customer]:
        """Busca clientes com base nos critérios fornecidos."""
        try:
            # Verificar se todos os campos têm o mesmo valor (busca genérica)
            search_values = [
                search_request.cpf,
                search_request.email,
                search_request.phone,
                search_request.name
            ]
            
            # Remover valores None
            non_none_values = [v for v in search_values if v is not None]
            
            # Se todos os valores não-None são iguais, fazer busca OR
            if len(set(non_none_values)) == 1 and len(non_none_values) > 1:
                # Busca genérica com OR
                search_term = non_none_values[0]
                query = {
                    "$or": [
                        {"cpf": search_term},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"phone": {"$regex": search_term, "$options": "i"}},
                        {"name": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            else:
                # Busca específica com AND
                query = {}
                
                if search_request.cpf:
                    query["cpf"] = search_request.cpf
                
                if search_request.email:
                    query["email"] = {"$regex": search_request.email, "$options": "i"}
                
                if search_request.phone:
                    query["phone"] = {"$regex": search_request.phone, "$options": "i"}
                
                if search_request.name:
                    query["name"] = {"$regex": search_request.name, "$options": "i"}
            
            # Se nenhum critério foi fornecido, retorna lista vazia
            if not query:
                return []
            
            cursor = self.collection.find(query).sort("created_at", -1)
            customers = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                customers.append(Customer(**doc))
            return customers
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            raise

    async def update(self, customer_id: str, update_data: dict) -> Optional[Customer]:
        """Atualiza um cliente."""
        try:
            if not ObjectId.is_valid(customer_id):
                return None
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                return await self.get_by_id(customer_id)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            raise

    async def delete(self, customer_id: str) -> bool:
        """Exclui um cliente (soft delete)."""
        try:
            if not ObjectId.is_valid(customer_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {"active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Erro ao excluir cliente: {e}")
            raise

    async def get_stats(self) -> CustomerStatsResponse:
        """Retorna estatísticas dos clientes."""
        try:
            # Total de clientes
            total_customers = await self.collection.count_documents({})
            
            # Clientes ativos
            active_customers = await self.collection.count_documents({"active": True})
            
            # Clientes inativos
            inactive_customers = total_customers - active_customers
            
            # Clientes cadastrados este mês
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            customers_this_month = await self.collection.count_documents({
                "created_at": {"$gte": start_of_month}
            })
            
            return CustomerStatsResponse(
                total_customers=total_customers,
                active_customers=active_customers,
                inactive_customers=inactive_customers,
                customers_this_month=customers_this_month
            )
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            raise

    async def create_indexes(self):
        """Cria índices para otimizar as consultas."""
        try:
            # Índice único para CPF
            await self.collection.create_index("cpf", unique=True)
            
            # Índice único para email
            await self.collection.create_index("email", unique=True)
            
            # Índice para telefone
            await self.collection.create_index("phone")
            
            # Índice para nome (para busca por texto)
            await self.collection.create_index("name")
            
            # Índice para data de criação
            await self.collection.create_index("created_at")
            
            # Índice para status ativo
            await self.collection.create_index("active")
            
            logger.info("Índices criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise 