#!/usr/bin/env python3
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para configurar o usuário admin no Keycloak
Resolve problemas de roles não encontradas e usuário admin não criado
"""

import asyncio
import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminSetup:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.admin_username = "admin"
        self.admin_password = "admin123"
        self.admin_client = None
        
    def connect_to_keycloak(self, retries=5):
        """Conecta ao Keycloak com retry"""
        for attempt in range(retries):
            try:
                self.admin_client = KeycloakAdmin(
                    server_url=self.keycloak_url,
                    username=self.admin_username,
                    password=self.admin_password,
                    realm_name="master",
                    verify=False
                )
                
                # Testa a conexão
                self.admin_client.get_realms()
                logger.info("✅ Conectado ao Keycloak com sucesso!")
                return True
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                    
        logger.error("❌ Falha ao conectar ao Keycloak após todas as tentativas")
        return False
    
    def setup_realm(self):
        """Configura o realm se não existir"""
        try:
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"🏗️  Criando realm: {self.realm_name}")
                realm_config = {
                    "realm": self.realm_name,
                    "displayName": "Vehicle Sales System",
                    "enabled": True,
                    "registrationAllowed": True,
                    "loginWithEmailAllowed": True,
                    "duplicateEmailsAllowed": False,
                    "resetPasswordAllowed": True,
                    "editUsernameAllowed": False,
                    "bruteForceProtected": True,
                    "accessTokenLifespan": 3600,
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"✅ Realm {self.realm_name} criado com sucesso")
            else:
                logger.info(f"ℹ️  Realm {self.realm_name} já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar realm: {e}")
            raise
    
    def setup_client(self):
        """Configura o client se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == "vehicle-sales-app" for client in clients)
            
            if not client_exists:
                logger.info("🏗️  Criando client: vehicle-sales-app")
                client_config = {
                    "clientId": "vehicle-sales-app",
                    "name": "Vehicle Sales Application",
                    "enabled": True,
                    "publicClient": False,
                    "bearerOnly": False,
                    "standardFlowEnabled": True,
                    "directAccessGrantsEnabled": True,
                    "serviceAccountsEnabled": True,
                    "authorizationServicesEnabled": True,
                    "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                    "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                    "attributes": {
                        "access.token.lifespan": "3600",
                        "client.session.idle.timeout": "3600",
                        "client.session.max.lifespan": "36000"
                    }
                }
                self.admin_client.create_client(client_config)
                logger.info("✅ Client vehicle-sales-app criado com sucesso")
            else:
                logger.info("ℹ️  Client vehicle-sales-app já existe")
                
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar client: {e}")
            raise
    
    def setup_roles(self):
        """Cria as roles necessárias"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Obtém roles existentes
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            # Roles necessárias
            required_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in required_roles:
                if role['name'] not in existing_role_names:
                    logger.info(f"🏗️  Criando role: {role['name']}")
                    self.admin_client.create_realm_role(role)
                    logger.info(f"✅ Role {role['name']} criada com sucesso")
                else:
                    logger.info(f"ℹ️  Role {role['name']} já existe")
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar roles: {e}")
            raise
    
    def setup_admin_user(self):
        """Cria o usuário admin se não existir"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Verifica se o usuário já existe
            admin_email = "admin@vehiclesales.com"
            users = self.admin_client.get_users({"email": admin_email})
            
            if users:
                logger.info(f"ℹ️  Usuário admin já existe: {admin_email}")
                user_id = users[0]['id']
            else:
                logger.info(f"🏗️  Criando usuário admin: {admin_email}")
                
                user_data = {
                    "username": admin_email,
                    "email": admin_email,
                    "firstName": "Admin",
                    "lastName": "System",
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [{
                        "type": "password",
                        "value": "admin123",
                        "temporary": False
                    }]
                }
                
                user_id = self.admin_client.create_user(user_data)
                logger.info(f"✅ Usuário admin criado com sucesso: {admin_email}")
            
            # Atribui role ADMIN ao usuário
            try:
                admin_role = self.admin_client.get_realm_role("ADMIN")
                current_roles = self.admin_client.get_realm_roles_of_user(user_id)
                current_role_names = [role['name'] for role in current_roles]
                
                if "ADMIN" not in current_role_names:
                    self.admin_client.assign_realm_roles(user_id, [admin_role])
                    logger.info("✅ Role ADMIN atribuída ao usuário admin")
                else:
                    logger.info("ℹ️  Usuário admin já possui role ADMIN")
                    
            except KeycloakError as e:
                logger.error(f"❌ Erro ao atribuir role ADMIN: {e}")
                raise
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao criar usuário admin: {e}")
            raise
    
    def run_setup(self):
        """Executa todo o processo de configuração"""
        logger.info("🚀 Iniciando configuração do Keycloak...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        try:
            # Configura realm
            self.setup_realm()
            
            # Configura client
            self.setup_client()
            
            # Configura roles
            self.setup_roles()
            
            # Cria usuário admin
            self.setup_admin_user()
            
            logger.info("✅ Configuração do Keycloak concluída com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante a configuração: {e}")
            return False

def main():
    """Função principal"""
    setup = AdminSetup()
    success = setup.run_setup()
    
    if success:
        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("🔐 Credenciais do Admin:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("="*60)
        print("🔗 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Keycloak: http://localhost:8080/admin")
        print("="*60)
    else:
        print("\n❌ Falha na configuração. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 