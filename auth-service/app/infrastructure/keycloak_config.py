from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class KeycloakConfig:
    def __init__(self):
        self.server_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.realm_name = os.getenv("KEYCLOAK_REALM", "vehicle-sales")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "vehicle-sales-app")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
        self.admin_username = os.getenv("KEYCLOAK_ADMIN", "admin")
        self.admin_password = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin123")
        
        self._admin_client = None
        self._openid_client = None
    
    @property
    def admin_client(self) -> KeycloakAdmin:
        if not self._admin_client:
            self._admin_client = KeycloakAdmin(
                server_url=self.server_url,
                username=self.admin_username,
                password=self.admin_password,
                realm_name="master",
                verify=False
            )
        return self._admin_client
    
    @property
    def openid_client(self) -> KeycloakOpenID:
        if not self._openid_client:
            self._openid_client = KeycloakOpenID(
                server_url=self.server_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                client_secret_key=self.client_secret,
                verify=False
            )
        return self._openid_client
    
    async def setup_realm_and_client(self):
        """Configura o realm e client no Keycloak se não existirem"""
        try:
            # Verificar se o realm existe
            realms = self.admin_client.get_realms()
            realm_exists = any(realm['realm'] == self.realm_name for realm in realms)
            
            if not realm_exists:
                logger.info(f"Criando realm: {self.realm_name}")
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
                    "accessTokenLifespan": 3600,  # 1 hora
                    "refreshTokenMaxReuse": 0,
                    "ssoSessionMaxLifespan": 36000,  # 10 horas
                }
                self.admin_client.create_realm(realm_config)
                logger.info(f"Realm {self.realm_name} criado com sucesso")
            
            # Configurar o client
            self.admin_client.realm_name = self.realm_name
            clients = self.admin_client.get_clients()
            client_exists = any(client['clientId'] == self.client_id for client in clients)
            
            if not client_exists:
                logger.info(f"Criando client: {self.client_id}")
                client_config = {
                    "clientId": self.client_id,
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
                client_id = self.admin_client.create_client(client_config)
                
                # Configurar client secret se necessário
                if self.client_secret:
                    client_data = self.admin_client.get_client(client_id)
                    client_data['secret'] = self.client_secret
                    self.admin_client.update_client(client_id, client_data)
                
                logger.info(f"Client {self.client_id} criado com sucesso")
            
            # Criar roles padrão
            await self._create_default_roles()
            
        except KeycloakError as e:
            logger.error(f"Erro ao configurar Keycloak: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao configurar Keycloak: {e}")
            raise
    
    async def _create_default_roles(self):
        """Cria roles padrão no realm"""
        try:
            self.admin_client.realm_name = self.realm_name
            existing_roles = self.admin_client.get_realm_roles()
            existing_role_names = [role['name'] for role in existing_roles]
            
            default_roles = [
                {"name": "ADMIN", "description": "Administrador do sistema"},
                {"name": "CUSTOMER", "description": "Cliente do sistema"},
                {"name": "SALES", "description": "Vendedor do sistema"}
            ]
            
            for role in default_roles:
                if role['name'] not in existing_role_names:
                    self.admin_client.create_realm_role(role)
                    logger.info(f"Role {role['name']} criada com sucesso")
            
        except KeycloakError as e:
            logger.error(f"Erro ao criar roles: {e}")
            raise
    
    async def create_user(self, email: str, password: str, name: str, role: str = "CUSTOMER") -> str:
        """Cria um usuário no Keycloak"""
        try:
            # Converter enum para string se necessário
            role_str = str(role.value) if hasattr(role, 'value') else str(role)
            
            # Salvar o realm original
            original_realm = self.admin_client.connection.realm_name
            
            # Configurar para o realm do sistema
            self.admin_client.connection.realm_name = self.realm_name
            
            user_data = {
                "username": email,
                "email": email,
                "firstName": name.split()[0] if name else "",
                "lastName": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False
                }]
            }
            
            user_id = self.admin_client.create_user(user_data)
            
            # Atribuir role ao usuário
            role_data = self.admin_client.get_realm_role(role_str)
            self.admin_client.assign_realm_roles(user_id, [role_data])
            
            logger.info(f"Usuário {email} criado com sucesso no Keycloak")
            return user_id
            
        except KeycloakError as e:
            logger.error(f"Erro ao criar usuário no Keycloak: {e}")
            raise
        finally:
            # Sempre restaurar o realm original
            if 'original_realm' in locals():
                self.admin_client.connection.realm_name = original_realm
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica um usuário no Keycloak"""
        try:
            token = self.openid_client.token(username=email, password=password)
            return token
        except KeycloakError as e:
            logger.error(f"Erro ao autenticar usuário: {e}")
            return None
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Valida um token no Keycloak"""
        try:
            token_info = self.openid_client.introspect(token)
            if token_info.get('active', False):
                return token_info
            return None
        except KeycloakError as e:
            logger.error(f"Erro ao validar token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Renova um token no Keycloak"""
        try:
            token = self.openid_client.refresh_token(refresh_token)
            return token
        except KeycloakError as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Faz logout de um usuário no Keycloak"""
        try:
            self.openid_client.logout(refresh_token)
            return True
        except KeycloakError as e:
            logger.error(f"Erro ao fazer logout: {e}")
            return False 