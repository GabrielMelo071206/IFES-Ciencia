import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch
from data.model.experimento_model import Experimento
from data.repo.experimento_repo import *
from data.sql.experimento_sql import CRIAR_TABELA_EXPERIMENTO


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
            cursor.execute(CRIAR_TABELA_EXPERIMENTO)
            conn.commit()


@pytest.fixture
def test_db():
    """Fixture para criar banco de dados de teste"""
    db = TestDatabase()
    db.setup_tables()
    
    # Mock da função get_connection
    with patch('data.repo.experimento_repo.get_connection', db.get_connection):
        yield db
    
    db.close()


class TestExperimentoRepo:
    
    def test_inserir_experimento(self, test_db):
        experimento = Experimento(
            id=0, titulo="Vulcão de Bicarbonato", 
            descricao="Experimento que simula um vulcão",
            materiais="bicarbonato, vinagre, corante",
            capa="vulcao.jpg", video_explicativo="video.mp4"
        )
        
        result = inserir_experimento(experimento)
        
        assert result is not None
        assert result > 0
    
    def test_obter_experimento_por_id(self, test_db):
        # Inserir primeiro
        experimento = Experimento(
            id=0, titulo="Vulcão de Bicarbonato", 
            descricao="Experimento que simula um vulcão",
            materiais="bicarbonato, vinagre, corante"
        )
        exp_id = inserir_experimento(experimento)
        
        # Buscar
        result = obter_experimento_por_id(exp_id)
        
        assert result is not None
        assert result.titulo == "Vulcão de Bicarbonato"
        assert result.descricao == "Experimento que simula um vulcão"
        assert result.materiais == "bicarbonato, vinagre, corante"
    
    def test_alterar_experimento(self, test_db):
        # Inserir primeiro
        experimento = Experimento(
            id=0, titulo="Vulcão", descricao="Teste", materiais="bicarbonato"
        )
        exp_id = inserir_experimento(experimento)
        
        # Alterar
        experimento_alterado = Experimento(
            id=exp_id, titulo="Vulcão Atualizado", 
            descricao="Descrição atualizada", materiais="bicarbonato, vinagre",
            capa="nova_capa.jpg", video_explicativo="novo_video.mp4"
        )
        result = alterar_experimento(experimento_alterado)
        
        assert result is True
        
        # Verificar alteração
        exp_verificado = obter_experimento_por_id(exp_id)
        assert exp_verificado.titulo == "Vulcão Atualizado"
        assert exp_verificado.descricao == "Descrição atualizada"
        assert exp_verificado.capa == "nova_capa.jpg"
    
    def test_excluir_experimento(self, test_db):
        # Inserir primeiro
        experimento = Experimento(id=0, titulo="Teste", descricao="Desc", materiais="Mat")
        exp_id = inserir_experimento(experimento)
        
        # Excluir
        result = excluir_experimento(exp_id)
        assert result is True
        
        # Verificar se foi excluído
        exp_verificado = obter_experimento_por_id(exp_id)
        assert exp_verificado is None
    
    def test_obter_todos_experimentos(self, test_db):
        # Inserir alguns experimentos
        exp1 = Experimento(id=0, titulo="Vulcão", descricao="Desc1", materiais="Mat1")
        exp2 = Experimento(id=0, titulo="Bateria", descricao="Desc2", materiais="Mat2")
        
        inserir_experimento(exp1)
        inserir_experimento(exp2)
        
        # Buscar todos
        result = obter_todos_experimentos()
        
        assert len(result) == 2
        # Verifica se está ordenado por título
        assert result[0].titulo == "Bateria"
        assert result[1].titulo == "Vulcão"
    
    def test_obter_experimento_por_titulo(self, test_db):
        # Inserir primeiro
        experimento = Experimento(id=0, titulo="Vulcão", descricao="Desc", materiais="Mat")
        inserir_experimento(experimento)
        
        # Buscar por título
        result = obter_experimento_por_titulo("Vulcão")
        
        assert result is not None
        assert result.titulo == "Vulcão"
    
    def test_buscar_experimentos_por_material(self, test_db):
        # Inserir experimentos com diferentes materiais
        exp1 = Experimento(id=0, titulo="Vulcão", descricao="Desc1", materiais="bicarbonato, vinagre")
        exp2 = Experimento(id=0, titulo="Bateria", descricao="Desc2", materiais="limão, fios")
        exp3 = Experimento(id=0, titulo="Slime", descricao="Desc3", materiais="cola, bicarbonato")
        
        inserir_experimento(exp1)
        inserir_experimento(exp2)
        inserir_experimento(exp3)
        
        # Buscar por material
        result = buscar_experimentos_por_material("bicarbonato")
        
        assert len(result) == 2
        assert all("bicarbonato" in exp.materiais for exp in result)
    
    def test_buscar_experimentos_por_descricao(self, test_db):
        # Inserir experimentos
        exp1 = Experimento(id=0, titulo="Vulcão", descricao="Experimento químico", materiais="Mat1")
        exp2 = Experimento(id=0, titulo="Bateria", descricao="Experimento físico", materiais="Mat2")
        exp3 = Experimento(id=0, titulo="Química Divertida", descricao="Teste", materiais="Mat3")
        
        inserir_experimento(exp1)
        inserir_experimento(exp2)
        inserir_experimento(exp3)
        
        # Buscar por termo na descrição ou título
        result = buscar_experimentos_por_descricao("químico")
        
        assert len(result) == 1
        assert result[0].descricao == "Experimento químico"
        
        # Buscar por termo no título
        result2 = buscar_experimentos_por_descricao("Química")
        assert len(result2) == 1
        assert result2[0].titulo == "Química Divertida"
    
    def test_titulo_existe(self, test_db):
        # Inserir primeiro
        experimento = Experimento(id=0, titulo="Vulcão", descricao="Desc", materiais="Mat")
        inserir_experimento(experimento)
        
        # Verificar se existe
        assert titulo_existe("Vulcão") is True
        assert titulo_existe("Inexistente") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])