#!/usr/bin/env python3
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para sincronizar o usuário admin do Keycloak para o MongoDB
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_admin_user():
    """Sincroniza o usuário admin do Keycloak para o MongoDB"""
    
    # Configuração do MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "auth_db")
    
    # Configuração do usuário admin
    admin_email = "admin@vehiclesales.com"
    admin_password = "admin123"
    admin_name = "Admin System"
    admin_role = "ADMIN"
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        logger.info("✅ Conectado ao MongoDB")
        
        # Verifica se o usuário admin já existe
        existing_user = await users_collection.find_one({"email": admin_email})
        
        if existing_user:
            logger.info(f"ℹ️  Usuário admin já existe no MongoDB: {admin_email}")
            return True
        
        # Cria hash da senha
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
        
        # Cria o documento do usuário
        user_doc = {
            "email": admin_email,
            "name": admin_name,
            "role": admin_role,
            "status": "ACTIVE",
            "password_hash": password_hash,
            "keycloak_id": "admin_keycloak_id",  # ID placeholder
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insere o usuário no MongoDB
        result = await users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"✅ Usuário admin criado no MongoDB: {admin_email}")
            return True
        else:
            logger.error("❌ Falha ao criar usuário admin no MongoDB")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar usuário admin: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

def main():
    """Função principal"""
    logger.info("🔄 Sincronizando usuário admin...")
    
    success = asyncio.run(sync_admin_user())
    
    if success:
        print("\n" + "="*60)
        print("✅ USUÁRIO ADMIN SINCRONIZADO COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🚀 Agora você pode executar:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na sincronização. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 