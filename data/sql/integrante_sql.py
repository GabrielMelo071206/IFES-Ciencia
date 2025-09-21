CRIAR_TABELA_INTEGRANTE = """
CREATE TABLE IF NOT EXISTS integrante (
    id_integrante   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,
    turma           TEXT    NOT NULL,
    funcao          TEXT    NOT NULL,
    foto            TEXT    NULL,
    redes_sociais   TEXT    NULL
);
"""

INSERIR_INTEGRANTE = """
INSERT INTO integrante (
    nome, turma, funcao, foto, redes_sociais
) VALUES (?, ?, ?, ?, ?);
"""

ALTERAR_INTEGRANTE = """
UPDATE integrante
SET nome=?, turma=?, funcao=?, foto=?, redes_sociais=?
WHERE id_integrante=?;
"""

EXCLUIR_INTEGRANTE = """
DELETE FROM integrante
WHERE id_integrante=?;
"""

OBTER_INTEGRANTE_POR_ID = """
SELECT 
    i.id_integrante,
    i.nome,
    i.turma,
    i.funcao,
    i.foto,
    i.redes_sociais
FROM integrante i
WHERE i.id_integrante = ?;
"""

OBTER_TODOS_INTEGRANTE = """
SELECT 
    i.id_integrante,
    i.nome,
    i.turma,
    i.funcao,
    i.foto,
    i.redes_sociais
FROM integrante i
ORDER BY i.nome;
"""

OBTER_INTEGRANTE_POR_NOME = """
SELECT 
    i.id_integrante,
    i.nome,
    i.turma,
    i.funcao,
    i.foto,
    i.redes_sociais
FROM integrante i
WHERE i.nome = ?;
"""
