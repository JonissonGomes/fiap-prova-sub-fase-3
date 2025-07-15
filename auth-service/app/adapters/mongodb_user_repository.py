from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.domain.user import User, UserRole, UserStatus

logger = logging.getLogger(__name__)

class MongoDBUserRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str = "auth_db", collection_name: str = "users"):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]
    
    async def create_user(self, user: User) -> User:
        """Cria um novo usuário no banco de dados"""
        try:
            user_dict = user.dict(exclude={'id'})
            user_dict['created_at'] = datetime.now()
            user_dict['updated_at'] = datetime.now()
            
            result = await self.collection.insert_one(user_dict)
            user.id = str(result.inserted_id)
            user.created_at = user_dict['created_at']
            user.updated_at = user_dict['updated_at']
            
            logger.info(f"Usuário {user.email} criado com sucesso")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca um usuário pelo ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo email"""
        try:
            user_data = await self.collection.find_one({"email": email})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            raise
    
    async def get_user_by_keycloak_id(self, keycloak_id: str) -> Optional[User]:
        """Busca um usuário pelo ID do Keycloak"""
        try:
            user_data = await self.collection.find_one({"keycloak_id": keycloak_id})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por Keycloak ID: {e}")
            raise
    
    async def update_user(self, user: User) -> User:
        """Atualiza um usuário no banco de dados"""
        try:
            if not ObjectId.is_valid(user.id):
                raise ValueError("ID do usuário inválido")
            
            update_data = user.dict(exclude={'id', 'created_at'})
            update_data['updated_at'] = datetime.now()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user.id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError("Usuário não encontrado")
            
            user.updated_at = update_data['updated_at']
            logger.info(f"Usuário {user.email} atualizado com sucesso")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Remove um usuário do banco de dados"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Usuário {user_id} removido com sucesso")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            raise
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista todos os usuários com paginação"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    async def list_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuários por papel"""
        try:
            cursor = self.collection.find({"role": role}).skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários por papel: {e}")
            raise
    
    async def list_users_by_status(self, status: UserStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuários por status"""
        try:
            cursor = self.collection.find({"status": status}).skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários por status: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> bool:
        """Atualiza o último login do usuário"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.now()}}
            )
            
            return result.matched_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao atualizar último login: {e}")
            raise
    
    async def count_users(self) -> int:
        """Conta o total de usuários"""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar usuários: {e}")
            raise
    
    async def email_exists(self, email: str) -> bool:
        """Verifica se um email já está em uso"""
        try:
            count = await self.collection.count_documents({"email": email})
            return count > 0
        except Exception as e:
            logger.error(f"Erro ao verificar email: {e}")
            raise 
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.domain.user import User, UserRole, UserStatus

logger = logging.getLogger(__name__)

class MongoDBUserRepository:
    def __init__(self, client: AsyncIOMotorClient, db_name: str = "auth_db", collection_name: str = "users"):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]
    
    async def create_user(self, user: User) -> User:
        """Cria um novo usuário no banco de dados"""
        try:
            user_dict = user.dict(exclude={'id'})
            user_dict['created_at'] = datetime.now()
            user_dict['updated_at'] = datetime.now()
            
            result = await self.collection.insert_one(user_dict)
            user.id = str(result.inserted_id)
            user.created_at = user_dict['created_at']
            user.updated_at = user_dict['updated_at']
            
            logger.info(f"Usuário {user.email} criado com sucesso")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Busca um usuário pelo ID"""
        try:
            if not ObjectId.is_valid(user_id):
                return None
            
            user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo email"""
        try:
            user_data = await self.collection.find_one({"email": email})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            raise
    
    async def get_user_by_keycloak_id(self, keycloak_id: str) -> Optional[User]:
        """Busca um usuário pelo ID do Keycloak"""
        try:
            user_data = await self.collection.find_one({"keycloak_id": keycloak_id})
            if user_data:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por Keycloak ID: {e}")
            raise
    
    async def update_user(self, user: User) -> User:
        """Atualiza um usuário no banco de dados"""
        try:
            if not ObjectId.is_valid(user.id):
                raise ValueError("ID do usuário inválido")
            
            update_data = user.dict(exclude={'id', 'created_at'})
            update_data['updated_at'] = datetime.now()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user.id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError("Usuário não encontrado")
            
            user.updated_at = update_data['updated_at']
            logger.info(f"Usuário {user.email} atualizado com sucesso")
            return user
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Remove um usuário do banco de dados"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Usuário {user_id} removido com sucesso")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            raise
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista todos os usuários com paginação"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    async def list_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuários por papel"""
        try:
            cursor = self.collection.find({"role": role}).skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários por papel: {e}")
            raise
    
    async def list_users_by_status(self, status: UserStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuários por status"""
        try:
            cursor = self.collection.find({"status": status}).skip(skip).limit(limit)
            users = []
            
            async for user_data in cursor:
                user_data['id'] = str(user_data['_id'])
                del user_data['_id']
                users.append(User(**user_data))
            
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários por status: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> bool:
        """Atualiza o último login do usuário"""
        try:
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.now()}}
            )
            
            return result.matched_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao atualizar último login: {e}")
            raise
    
    async def count_users(self) -> int:
        """Conta o total de usuários"""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar usuários: {e}")
            raise
    
    async def email_exists(self, email: str) -> bool:
        """Verifica se um email já está em uso"""
        try:
            count = await self.collection.count_documents({"email": email})
            return count > 0
        except Exception as e:
            logger.error(f"Erro ao verificar email: {e}")
            raise 