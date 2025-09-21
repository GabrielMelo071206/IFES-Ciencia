CRIAR_TABELA_ADMINISTRADOR = """
CREATE TABLE IF NOT EXISTS administrador (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email TEXT NOT NULL,
    senha TEXT NOT NULL
    );
"""

INSERIR_ADMINISTRADOR = """
INSERT INTO administrador (
    email, senha
) VALUES (?, ?);
"""

ALTERAR_ADMINISTRADOR = """
UPDATE administrador
SET email=?, senha=?
WHERE id=?;
"""

EXCLUIR_ADMINISTRADOR = """
DELETE FROM administrador
WHERE id=?;
"""

OBTER_POR_ID_ADMINISTRADOR = """
SELECT 
    id, email, senha
FROM administrador
WHERE id=?;
"""

OBTER_TODOS_ADMINISTRADOR = """
SELECT 
    id, email, senha 
FROM administrador
ORDER BY id;
"""