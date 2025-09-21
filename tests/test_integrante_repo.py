import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch
from data.model.integrante_model import Integrante
from data.repo.integrante_repo import *
from data.sql.integrante_sql import CRIAR_TABELA_INTEGRANTE


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
            cursor.execute(CRIAR_TABELA_INTEGRANTE)
            conn.commit()


@pytest.fixture
def test_db():
    """Fixture para criar banco de dados de teste"""
    db = TestDatabase()
    db.setup_tables()
    
    # Mock da função get_connection
    with patch('data.repo.integrante_repo.get_connection', db.get_connection):
        yield db
    
    db.close()


class TestIntegranteRepo:
    
    def test_inserir_integrante(self, test_db):
        integrante = Integrante(
            id=0, nome="João Silva", turma="3A", 
            funcao="Desenvolvedor", foto="foto.jpg", redes_sociais="@joao"
        )
        
        result = inserir_integrante(integrante)
        
        assert result is not None
        assert result > 0
    
    def test_obter_integrante_por_id(self, test_db):
        # Inserir primeiro
        integrante = Integrante(
            id=0, nome="João Silva", turma="3A", 
            funcao="Desenvolvedor", foto="foto.jpg", redes_sociais="@joao"
        )
        integrante_id = inserir_integrante(integrante)
        
        # Buscar
        result = obter_integrante_por_id(integrante_id)
        
        assert result is not None
        assert result.nome == "João Silva"
        assert result.turma == "3A"
        assert result.funcao == "Desenvolvedor"
        assert result.foto == "foto.jpg"
        assert result.redes_sociais == "@joao"
    
    def test_alterar_integrante(self, test_db):
        # Inserir primeiro
        integrante = Integrante(
            id=0, nome="João Silva", turma="3A", 
            funcao="Desenvolvedor"
        )
        integrante_id = inserir_integrante(integrante)
        
        # Alterar
        integrante_alterado = Integrante(
            id=integrante_id, nome="João Santos", turma="3B", 
            funcao="Designer", foto="nova_foto.jpg", redes_sociais="@joaosantos"
        )
        result = alterar_integrante(integrante_alterado)
        
        assert result is True
        
        # Verificar alteração
        integrante_verificado = obter_integrante_por_id(integrante_id)
        assert integrante_verificado.nome == "João Santos"
        assert integrante_verificado.turma == "3B"
        assert integrante_verificado.funcao == "Designer"
    
    def test_excluir_integrante(self, test_db):
        # Inserir primeiro
        integrante = Integrante(id=0, nome="João Silva", turma="3A", funcao="Dev")
        integrante_id = inserir_integrante(integrante)
        
        # Excluir
        result = excluir_integrante(integrante_id)
        assert result is True
        
        # Verificar se foi excluído
        integrante_verificado = obter_integrante_por_id(integrante_id)
        assert integrante_verificado is None
    
    def test_obter_todos_integrantes(self, test_db):
        # Inserir alguns integrantes
        integrante1 = Integrante(id=0, nome="Ana", turma="3A", funcao="Dev")
        integrante2 = Integrante(id=0, nome="Bruno", turma="3B", funcao="Designer")
        
        inserir_integrante(integrante1)
        inserir_integrante(integrante2)
        
        # Buscar todos
        result = obter_todos_integrantes()
        
        assert len(result) == 2
        # Verifica se está ordenado por nome
        assert result[0].nome == "Ana"
        assert result[1].nome == "Bruno"
    
    def test_obter_integrante_por_nome(self, test_db):
        # Inserir primeiro
        integrante = Integrante(id=0, nome="João Silva", turma="3A", funcao="Dev")
        inserir_integrante(integrante)
        
        # Buscar por nome
        result = obter_integrante_por_nome("João Silva")
        
        assert result is not None
        assert result.nome == "João Silva"
    
    def test_obter_integrantes_por_turma(self, test_db):
        # Inserir integrantes de diferentes turmas
        integrante1 = Integrante(id=0, nome="Ana", turma="3A", funcao="Dev")
        integrante2 = Integrante(id=0, nome="Bruno", turma="3A", funcao="Designer")
        integrante3 = Integrante(id=0, nome="Carlos", turma="3B", funcao="Dev")
        
        inserir_integrante(integrante1)
        inserir_integrante(integrante2)
        inserir_integrante(integrante3)
        
        # Buscar por turma
        result = obter_integrantes_por_turma("3A")
        
        assert len(result) == 2
        assert all(i.turma == "3A" for i in result)
    
    def test_obter_integrantes_por_funcao(self, test_db):
        # Inserir integrantes com diferentes funções
        integrante1 = Integrante(id=0, nome="Ana", turma="3A", funcao="Dev")
        integrante2 = Integrante(id=0, nome="Bruno", turma="3B", funcao="Dev")
        integrante3 = Integrante(id=0, nome="Carlos", turma="3A", funcao="Designer")
        
        inserir_integrante(integrante1)
        inserir_integrante(integrante2)
        inserir_integrante(integrante3)
        
        # Buscar por função
        result = obter_integrantes_por_funcao("Dev")
        
        assert len(result) == 2
        assert all(i.funcao == "Dev" for i in result)
    
    def test_nome_existe(self, test_db):
        # Inserir primeiro
        integrante = Integrante(id=0, nome="João Silva", turma="3A", funcao="Dev")
        inserir_integrante(integrante)
        
        # Verificar se existe
        assert nome_existe("João Silva") is True
        assert nome_existe("Maria Silva") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])