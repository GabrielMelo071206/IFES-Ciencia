CRIAR_TABELA_EXPERIMENTO = """
CREATE TABLE IF NOT EXISTS experimento (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo               TEXT    NOT NULL,
    descricao            TEXT    NOT NULL,
    materiais            TEXT    NOT NULL,
    capa                 TEXT    NULL,
    video_explicativo    TEXT    NULL
);
"""

INSERIR_EXPERIMENTO = """
INSERT INTO experimento (
    titulo, descricao, materiais, capa, video_explicativo
) VALUES (?, ?, ?, ?, ?);
"""

ALTERAR_EXPERIMENTO = """
UPDATE experimento
SET titulo=?, descricao=?, materiais=?, capa=?, video_explicativo=?
WHERE id=?;
"""

EXCLUIR_EXPERIMENTO = """
DELETE FROM experimento
WHERE id=?;
"""

OBTER_EXPERIMENTO_POR_ID = """
SELECT 
    e.id,
    e.titulo,
    e.descricao,
    e.materiais,
    e.capa,
    e.video_explicativo
FROM experimento e
WHERE e.id = ?;
"""

OBTER_TODOS_EXPERIMENTO = """
SELECT 
    e.id,
    e.titulo,
    e.descricao,
    e.materiais,
    e.capa,
    e.video_explicativo
FROM experimento e
ORDER BY e.titulo;
"""

OBTER_EXPERIMENTO_POR_TITULO = """
SELECT 
    e.id,
    e.titulo,
    e.descricao,
    e.materiais,
    e.capa,
    e.video_explicativo
FROM experimento e
WHERE e.titulo = ?;
"""
 