#!/usr/bin/env python3
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para corrigir a configuração do client no Keycloak
Habilita direct access grants e configura corretamente o client
"""

import time
import logging
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientFix:
    def __init__(self):
        self.keycloak_url = "http://keycloak:8080"
        self.realm_name = "vehicle-sales"
        self.client_id = "vehicle-sales-app"
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
    
    def fix_client_configuration(self):
        """Corrige a configuração do client"""
        try:
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            client = None
            for c in clients:
                if c['clientId'] == self.client_id:
                    client = c
                    break
            
            if not client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            logger.info(f"🔍 Client encontrado: {client['id']}")
            
            # Configurações necessárias
            client_config = {
                "id": client['id'],
                "clientId": self.client_id,
                "enabled": True,
                "publicClient": True,  # IMPORTANTE: Public client para não precisar de secret
                "bearerOnly": False,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,  # IMPORTANTE: Habilita password grant
                "serviceAccountsEnabled": False,  # Não precisa para public client
                "authorizationServicesEnabled": False,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:8002/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:8002"],
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client.session.idle.timeout": "3600",
                    "client.session.max.lifespan": "36000",
                    "post.logout.redirect.uris": "+"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client['id'], client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se a configuração foi aplicada
            updated_client = self.admin_client.get_client(client['id'])
            if updated_client['directAccessGrantsEnabled']:
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️  Direct Access Grants ainda não está habilitado")
            
            return True
            
        except KeycloakError as e:
            logger.error(f"❌ Erro ao corrigir client: {e}")
            return False
    
    def test_client_configuration(self):
        """Testa se o client está configurado corretamente"""
        try:
            from keycloak import KeycloakOpenID
            
            # Testa conexão com o client
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                verify=False
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Login de teste falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def run_fix(self):
        """Executa a correção"""
        logger.info("🔧 Iniciando correção da configuração do client...")
        
        # Conecta ao Keycloak
        if not self.connect_to_keycloak():
            return False
        
        # Corrige a configuração do client
        if not self.fix_client_configuration():
            return False
        
        # Testa a configuração
        if not self.test_client_configuration():
            logger.warning("⚠️  Configuração aplicada, mas teste falhou")
            return False
        
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    fix = ClientFix()
    success = fix.run_fix()
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("="*60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("="*60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("="*60)
    else:
        print("\n❌ Falha na correção. Verifique os logs acima.")
        exit(1)

if __name__ == "__main__":
    main() 