import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch
from data.model.administrador_model import Administrador
from data.repo.administrador_repo import *
from data.sql.administrador_sql import CRIAR_TABELA_ADMINISTRADOR


class TestDatabase:
    """Classe para gerenciar banco de dados de teste"""
    
    def __init__(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.connection = None
    
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def setup_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CRIAR_TABELA_ADMINISTRADOR)
            conn.commit()


@pytest.fixture
def test_db():
    """Fixture para criar banco de dados de teste"""
    db = TestDatabase()
    db.setup_tables()
    
    # Mock da função get_connection
    with patch('data.repo.administrador_repo.get_connection', db.get_connection):
        yield db
    
    db.close()


class TestAdministradorRepo:
    
    def test_inserir_administrador(self, test_db):
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        
        result = inserir_administrador(admin)
        
        assert result is not None
        assert result > 0
    
    def test_obter_administrador_por_id(self, test_db):
        # Inserir primeiro
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        admin_id = inserir_administrador(admin)
        
        # Buscar
        result = obter_administrador_por_id(admin_id)
        
        assert result is not None
        assert result.email == "admin@test.com"
        assert result.senha == "123456"
        assert result.id == admin_id
    
    def test_obter_administrador_por_id_inexistente(self, test_db):
        result = obter_administrador_por_id(999)
        assert result is None
    
    def test_alterar_administrador(self, test_db):
        # Inserir primeiro
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        admin_id = inserir_administrador(admin)
        
        # Alterar
        admin_alterado = Administrador(id=admin_id, email="novo@test.com", senha="654321")
        result = alterar_administrador(admin_alterado)
        
        assert result is True
        
        # Verificar alteração
        admin_verificado = obter_administrador_por_id(admin_id)
        assert admin_verificado.email == "novo@test.com"
        assert admin_verificado.senha == "654321"
    
    def test_alterar_administrador_inexistente(self, test_db):
        admin = Administrador(id=999, email="admin@test.com", senha="123456")
        result = alterar_administrador(admin)
        assert result is False
    
    def test_excluir_administrador(self, test_db):
        # Inserir primeiro
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        admin_id = inserir_administrador(admin)
        
        # Excluir
        result = excluir_administrador(admin_id)
        assert result is True
        
        # Verificar se foi excluído
        admin_verificado = obter_administrador_por_id(admin_id)
        assert admin_verificado is None
    
    def test_excluir_administrador_inexistente(self, test_db):
        result = excluir_administrador(999)
        assert result is False
    
    def test_obter_todos_administradores(self, test_db):
        # Inserir alguns administradores
        admin1 = Administrador(id=0, email="admin1@test.com", senha="123")
        admin2 = Administrador(id=0, email="admin2@test.com", senha="456")
        
        inserir_administrador(admin1)
        inserir_administrador(admin2)
        
        # Buscar todos
        result = obter_todos_administradores()
        
        assert len(result) == 2
        assert any(a.email == "admin1@test.com" for a in result)
        assert any(a.email == "admin2@test.com" for a in result)
    
    def test_obter_administrador_por_email(self, test_db):
        # Inserir primeiro
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        inserir_administrador(admin)
        
        # Buscar por email
        result = obter_administrador_por_email("admin@test.com")
        
        assert result is not None
        assert result.email == "admin@test.com"
        assert result.senha == "123456"
    
    def test_obter_administrador_por_email_inexistente(self, test_db):
        result = obter_administrador_por_email("inexistente@test.com")
        assert result is None
    
    def test_email_existe(self, test_db):
        # Inserir primeiro
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        inserir_administrador(admin)
        
        # Verificar se existe
        assert email_existe("admin@test.com") is True
        assert email_existe("inexistente@test.com") is False
    
    def test_email_existe_excluindo_id(self, test_db):
        # Inserir administrador
        admin = Administrador(id=0, email="admin@test.com", senha="123456")
        admin_id = inserir_administrador(admin)
        
        # Verificar excluindo o próprio ID (para updates)
        assert email_existe("admin@test.com", admin_id) is False
        assert email_existe("admin@test.com") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])