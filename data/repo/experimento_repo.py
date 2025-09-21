from typing import Optional, List
from data.model.experimento_model import Experimento
from data.sql.experimento_sql import *
from util.db_util import get_connection


def inserir_experimento(experimento: Experimento) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR_EXPERIMENTO, (
            experimento.titulo,
            experimento.descricao,
            experimento.materiais,
            experimento.capa,
            experimento.video_explicativo
        ))
        conn.commit()
        return cursor.lastrowid


def alterar_experimento(experimento: Experimento) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR_EXPERIMENTO,
            (
                experimento.titulo,
                experimento.descricao,
                experimento.materiais,
                experimento.capa,
                experimento.video_explicativo,
                experimento.id
            )
        )
        conn.commit()
        return cursor.rowcount > 0


def excluir_experimento(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_EXPERIMENTO, (id,))
        conn.commit()
        return cursor.rowcount > 0


def obter_experimento_por_id(id: int) -> Optional[Experimento]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_EXPERIMENTO_POR_ID, (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Experimento(
            id=row["id"],
            titulo=row["titulo"],
            descricao=row["descricao"],
            materiais=row["materiais"],
            capa=row["capa"],
            video_explicativo=row["video_explicativo"]
        )


def obter_todos_experimentos() -> List[Experimento]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_EXPERIMENTO)
        rows = cursor.fetchall()
        return [
            Experimento(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                materiais=row["materiais"],
                capa=row["capa"],
                video_explicativo=row["video_explicativo"]
            )
            for row in rows
        ]


def obter_experimento_por_titulo(titulo: str) -> Optional[Experimento]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_EXPERIMENTO_POR_TITULO, (titulo,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Experimento(
            id=row["id"],
            titulo=row["titulo"],
            descricao=row["descricao"],
            materiais=row["materiais"],
            capa=row["capa"],
            video_explicativo=row["video_explicativo"]
        )


def buscar_experimentos_por_material(material: str) -> List[Experimento]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, titulo, descricao, materiais, capa, video_explicativo FROM experimento WHERE materiais LIKE ? ORDER BY titulo",
            (f"%{material}%",)
        )
        rows = cursor.fetchall()
        return [
            Experimento(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                materiais=row["materiais"],
                capa=row["capa"],
                video_explicativo=row["video_explicativo"]
            )
            for row in rows
        ]


def buscar_experimentos_por_descricao(termo: str) -> List[Experimento]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, titulo, descricao, materiais, capa, video_explicativo FROM experimento WHERE descricao LIKE ? OR titulo LIKE ? ORDER BY titulo",
            (f"%{termo}%", f"%{termo}%")
        )
        rows = cursor.fetchall()
        return [
            Experimento(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                materiais=row["materiais"],
                capa=row["capa"],
                video_explicativo=row["video_explicativo"]
            )
            for row in rows
        ]


def titulo_existe(titulo: str, excluir_id: Optional[int] = None) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        if excluir_id:
            cursor.execute(
                "SELECT COUNT(*) as count FROM experimento WHERE titulo = ? AND id != ?",
                (titulo, excluir_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM experimento WHERE titulo = ?",
                (titulo,)
            )
        return cursor.fetchone()["count"] > 0