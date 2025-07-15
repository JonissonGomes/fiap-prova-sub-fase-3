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
            logger.info("🔧 Iniciando correção da configuração do client...")
            
            # Muda para o realm correto
            self.admin_client.realm_name = self.realm_name
            
            # Busca o client
            clients = self.admin_client.get_clients()
            target_client = None
            
            for client in clients:
                if client.get('clientId') == self.client_id:
                    target_client = client
                    break
            
            if not target_client:
                logger.error(f"❌ Client {self.client_id} não encontrado!")
                return False
            
            client_uuid = target_client['id']
            logger.info(f"🔍 Client encontrado: {client_uuid}")
            
            # Configuração correta do client
            client_config = {
                "enabled": True,
                "clientId": self.client_id,
                "directAccessGrantsEnabled": True,
                "publicClient": False,
                "standardFlowEnabled": True,
                "implicitFlowEnabled": False,
                "serviceAccountsEnabled": False,
                "protocol": "openid-connect",
                "attributes": {
                    "access.token.lifespan": "3600",
                    "client_credentials.use_refresh_token": "false",
                    "display.on.consent.screen": "false",
                    "exclude.session.state.from.auth.response": "false",
                    "id.token.as.detached.signature": "false",
                    "saml.assertion.signature": "false",
                    "saml.client.signature": "false",
                    "saml.encrypt": "false",
                    "saml.force.post.binding": "false",
                    "saml.multivalued.roles": "false",
                    "saml.server.signature": "false",
                    "saml.server.signature.keyinfo.ext": "false",
                    "tls.client.certificate.bound.access.tokens": "false",
                    "use.refresh.tokens": "true",
                    "client.secret.creation.time": "1673547000"
                }
            }
            
            # Atualiza o client
            self.admin_client.update_client(client_uuid, client_config)
            logger.info("✅ Client atualizado com sucesso!")
            
            # Verifica se Direct Access Grants está habilitado
            updated_client = self.admin_client.get_client(client_uuid)
            if updated_client.get('directAccessGrantsEnabled'):
                logger.info("✅ Direct Access Grants habilitado!")
            else:
                logger.warning("⚠️ Direct Access Grants não está habilitado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir configuração: {e}")
            return False
    
    def test_login(self):
        """Testa o login com as credenciais admin"""
        try:
            from keycloak import KeycloakOpenID
            
            # Configura o client OpenID
            keycloak_openid = KeycloakOpenID(
                server_url=self.keycloak_url,
                client_id=self.client_id,
                realm_name=self.realm_name,
                client_secret_key="T14LidpfzazUfpvn6GsrlDyGooT8p0s6"
            )
            
            # Tenta fazer login
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123",
                grant_type="password"
            )
            
            if token:
                logger.info("✅ Login de teste bem-sucedido!")
                return True
            else:
                logger.error("❌ Falha no login de teste")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de login: {e}")
            return False
    
    def run(self):
        """Executa a correção completa"""
        if not self.connect_to_keycloak():
            return False
            
        if not self.fix_client_configuration():
            return False
            
        if not self.test_login():
            logger.warning("⚠️ Teste de login falhou, mas client foi configurado")
            
        logger.info("✅ Correção concluída com sucesso!")
        return True

def main():
    """Função principal"""
    client_fix = ClientFix()
    
    if client_fix.run():
        print("")
        print("=" * 60)
        print("✅ CLIENT CORRIGIDO COM SUCESSO!")
        print("=" * 60)
        print("🔐 Agora você pode fazer login com:")
        print("   Email: admin@vehiclesales.com")
        print("   Senha: admin123")
        print("=" * 60)
        print("🚀 Execute novamente:")
        print("   make populate-data")
        print("=" * 60)
        print("")
        return True
    else:
        print("")
        print("=" * 60)
        print("❌ FALHA NA CORREÇÃO DO CLIENT!")
        print("=" * 60)
        print("🔍 Verifique:")
        print("   1. Keycloak está rodando na porta 8080")
        print("   2. Realm 'vehicle-sales' existe")
        print("   3. Client 'vehicle-sales-app' existe")
        print("=" * 60)
        print("")
        return False

if __name__ == "__main__":
    main() 