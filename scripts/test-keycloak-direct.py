#!/usr/bin/env python3
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 
"""
Script para testar diretamente o Keycloak e diagnosticar problemas
"""

import logging
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keycloak():
    """Testa configuração do Keycloak"""
    keycloak_url = "http://keycloak:8080"
    realm_name = "vehicle-sales"
    client_id = "vehicle-sales-app"
    
    try:
        # Testa conexão admin
        admin_client = KeycloakAdmin(
            server_url=keycloak_url,
            username="admin",
            password="admin123",
            realm_name="master",
            verify=False
        )
        
        logger.info("✅ Conectado ao Keycloak como admin")
        
        # Lista realms
        realms = admin_client.get_realms()
        logger.info(f"📋 Realms disponíveis: {[r['realm'] for r in realms]}")
        
        # Verifica se o realm existe
        if realm_name not in [r['realm'] for r in realms]:
            logger.error(f"❌ Realm {realm_name} não encontrado!")
            return False
        
        # Configura para o realm correto
        admin_client.realm_name = realm_name
        
        # Lista clients
        clients = admin_client.get_clients()
        client = None
        for c in clients:
            if c['clientId'] == client_id:
                client = c
                break
        
        if not client:
            logger.error(f"❌ Client {client_id} não encontrado!")
            return False
        
        logger.info(f"✅ Client encontrado: {client['clientId']}")
        logger.info(f"📋 Direct Access Grants: {client.get('directAccessGrantsEnabled', False)}")
        logger.info(f"📋 Public Client: {client.get('publicClient', False)}")
        logger.info(f"📋 Enabled: {client.get('enabled', False)}")
        
        # Lista usuários
        users = admin_client.get_users()
        admin_user = None
        for u in users:
            if u['email'] == 'admin@vehiclesales.com':
                admin_user = u
                break
        
        if not admin_user:
            logger.error("❌ Usuário admin não encontrado!")
            return False
        
        logger.info(f"✅ Usuário admin encontrado: {admin_user['username']}")
        logger.info(f"📋 Enabled: {admin_user.get('enabled', False)}")
        logger.info(f"📋 Email Verified: {admin_user.get('emailVerified', False)}")
        
        # Verifica roles do usuário
        user_roles = admin_client.get_realm_roles_of_user(admin_user['id'])
        logger.info(f"📋 Roles do usuário: {[r['name'] for r in user_roles]}")
        
        # Testa login direto
        logger.info("🔐 Testando login direto...")
        
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=False
        )
        
        try:
            token = keycloak_openid.token(
                username="admin@vehiclesales.com",
                password="admin123"
            )
            
            if token:
                logger.info("✅ Login direto bem-sucedido!")
                logger.info(f"📋 Token type: {token.get('token_type')}")
                return True
            else:
                logger.error("❌ Login direto falhou - token vazio")
                return False
                
        except KeycloakError as e:
            logger.error(f"❌ Erro no login direto: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Testando configuração do Keycloak...")
    
    success = test_keycloak()
    
    if success:
        print("\n✅ Keycloak está configurado corretamente!")
    else:
        print("\n❌ Problemas encontrados na configuração do Keycloak")
        exit(1)

if __name__ == "__main__":
    main() 