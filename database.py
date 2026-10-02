import sqlite3

def conectar():
    return sqlite3.connect("database.db")


def criar_banco():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            discord_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            pontos INTEGER DEFAULT 0,
            quizzes_respondidos INTEGER DEFAULT 0,
            acertos INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER NOT NULL,
            quiz_id TEXT NOT NULL,
            resposta TEXT NOT NULL,
            correta INTEGER NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    banco.commit()
    banco.close()


def criar_usuario(discord_id, nome):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (
            discord_id,
            nome
        )
        VALUES (?, ?)
    """, (
        discord_id,
        nome
    ))

    cursor.execute("""
        UPDATE usuarios
        SET nome = ?
        WHERE discord_id = ?
    """, (
        nome,
        discord_id
    ))

    banco.commit()
    banco.close()


def salvar_resposta(
    discord_id,
    quiz_id,
    resposta,
    correta
):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        INSERT INTO respostas (
            discord_id,
            quiz_id,
            resposta,
            correta
        )
        VALUES (?, ?, ?, ?)
    """, (
        discord_id,
        quiz_id,
        resposta,
        1 if correta else 0
    ))

    cursor.execute("""
        UPDATE usuarios
        SET quizzes_respondidos = quizzes_respondidos + 1
        WHERE discord_id = ?
    """, (
        discord_id,
    ))

    if correta:

        cursor.execute("""
            UPDATE usuarios
            SET pontos = pontos + 20,
                acertos = acertos + 1
            WHERE discord_id = ?
        """, (
            discord_id,
        ))

    banco.commit()
    banco.close()


def ranking(limite=3):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""
        SELECT
            discord_id,
            nome,
            pontos
        FROM usuarios
        ORDER BY pontos DESC
        LIMIT ?
    """, (
        limite,
    ))

    resultados = cursor.fetchall()

    banco.close()

    return resultados


criar_banco()