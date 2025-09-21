from typing import Optional, List
from data.model.administrador_model import Administrador
from data.sql.administrador_sql import *
from util.db_util import get_connection


def inserir_administrador(admin: Administrador) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR_ADMINISTRADOR, (admin.email, admin.senha))
        conn.commit()
        return cursor.lastrowid


def alterar_administrador(admin: Administrador) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR_ADMINISTRADOR,
            (admin.email, admin.senha, admin.id)
        )
        conn.commit()
        return cursor.rowcount > 0


def excluir_administrador(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_ADMINISTRADOR, (id,))
        conn.commit()
        return cursor.rowcount > 0


def obter_administrador_por_id(id: int) -> Optional[Administrador]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID_ADMINISTRADOR, (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Administrador(
            id=row["id"],
            email=row["email"],
            senha=row["senha"]
        )


def obter_todos_administradores() -> List[Administrador]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_ADMINISTRADOR)
        rows = cursor.fetchall()
        return [
            Administrador(
                id=row["id"],
                email=row["email"],
                senha=row["senha"]
            )
            for row in rows
        ]


def obter_administrador_por_email(email: str) -> Optional[Administrador]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, senha FROM administrador WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Administrador(
            id=row["id"],
            email=row["email"],
            senha=row["senha"]
        )


def email_existe(email: str, excluir_id: Optional[int] = None) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        if excluir_id:
            cursor.execute(
                "SELECT COUNT(*) as count FROM administrador WHERE email = ? AND id != ?",
                (email, excluir_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM administrador WHERE email = ?",
                (email,)
            )
        return cursor.fetchone()["count"] > 0