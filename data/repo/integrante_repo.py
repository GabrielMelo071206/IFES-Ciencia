from typing import Optional, List
from data.model.integrante_model import Integrante
from data.sql.integrante_sql import *
from util.db_util import get_connection


def inserir_integrante(integrante: Integrante) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR_INTEGRANTE, (
            integrante.nome,
            integrante.turma,
            integrante.funcao,
            integrante.foto,
            integrante.redes_sociais
        ))
        conn.commit()
        return cursor.lastrowid


def alterar_integrante(integrante: Integrante) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ALTERAR_INTEGRANTE,
            (
                integrante.nome,
                integrante.turma,
                integrante.funcao,
                integrante.foto,
                integrante.redes_sociais,
                integrante.id
            )
        )
        conn.commit()
        return cursor.rowcount > 0


def excluir_integrante(id_integrante: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_INTEGRANTE, (id_integrante,))
        conn.commit()
        return cursor.rowcount > 0


def obter_integrante_por_id(id_integrante: int) -> Optional[Integrante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_INTEGRANTE_POR_ID, (id_integrante,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Integrante(
            id=row["id_integrante"],
            nome=row["nome"],
            turma=row["turma"],
            funcao=row["funcao"],
            foto=row["foto"],
            redes_sociais=row["redes_sociais"]
        )


def obter_todos_integrantes() -> List[Integrante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_INTEGRANTE)
        rows = cursor.fetchall()
        return [
            Integrante(
                id=row["id_integrante"],
                nome=row["nome"],
                turma=row["turma"],
                funcao=row["funcao"],
                foto=row["foto"],
                redes_sociais=row["redes_sociais"]
            )
            for row in rows
        ]


def obter_integrante_por_nome(nome: str) -> Optional[Integrante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_INTEGRANTE_POR_NOME, (nome,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Integrante(
            id=row["id_integrante"],
            nome=row["nome"],
            turma=row["turma"],
            funcao=row["funcao"],
            foto=row["foto"],
            redes_sociais=row["redes_sociais"]
        )


def obter_integrantes_por_turma(turma: str) -> List[Integrante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_integrante, nome, turma, funcao, foto, redes_sociais FROM integrante WHERE turma = ? ORDER BY nome",
            (turma,)
        )
        rows = cursor.fetchall()
        return [
            Integrante(
                id=row["id_integrante"],
                nome=row["nome"],
                turma=row["turma"],
                funcao=row["funcao"],
                foto=row["foto"],
                redes_sociais=row["redes_sociais"]
            )
            for row in rows
        ]


def obter_integrantes_por_funcao(funcao: str) -> List[Integrante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_integrante, nome, turma, funcao, foto, redes_sociais FROM integrante WHERE funcao = ? ORDER BY nome",
            (funcao,)
        )
        rows = cursor.fetchall()
        return [
            Integrante(
                id=row["id_integrante"],
                nome=row["nome"],
                turma=row["turma"],
                funcao=row["funcao"],
                foto=row["foto"],
                redes_sociais=row["redes_sociais"]
            )
            for row in rows
        ]


def nome_existe(nome: str, excluir_id: Optional[int] = None) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        if excluir_id:
            cursor.execute(
                "SELECT COUNT(*) as count FROM integrante WHERE nome = ? AND id_integrante != ?",
                (nome, excluir_id)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM integrante WHERE nome = ?",
                (nome,)
            )
        return cursor.fetchone()["count"] > 0