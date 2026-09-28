"""Painel local para registrar problemas de usabilidade com Flask e SQLite."""

from contextlib import closing
from pathlib import Path
import os
import secrets
import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, url_for


CAMINHO_BANCO = Path(__file__).with_name("problemas.db")
CATEGORIAS = ("navegacao", "formulario", "feedback", "acessibilidade", "outro")
GRAVIDADES = ("baixa", "media", "alta")
CAMPOS = ("titulo", "sistema", "categoria", "gravidade", "descricao")
ROTULOS = {
    "titulo": "Título",
    "sistema": "Sistema",
    "categoria": "Categoria",
    "gravidade": "Gravidade",
    "descricao": "Descrição",
}


def conectar(caminho_banco):
    """Abre uma conexão cujas linhas podem ser lidas pelo nome da coluna."""
    conexao = sqlite3.connect(caminho_banco)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco(caminho_banco=CAMINHO_BANCO):
    """Cria a tabela se necessário; pode ser chamada repetidas vezes."""
    with closing(conectar(caminho_banco)) as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS problemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                sistema TEXT NOT NULL,
                categoria TEXT NOT NULL,
                gravidade TEXT NOT NULL,
                descricao TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        conexao.commit()


def dados_do_formulario(formulario):
    """Remove espaços de todos os campos antes da validação."""
    return {campo: formulario.get(campo, "").strip() for campo in CAMPOS}


def validar(dados):
    """Retorna erros legíveis, indexados pelo campo correspondente."""
    erros = {}
    for campo in CAMPOS:
        if not dados[campo]:
            erros[campo] = f'O campo "{ROTULOS[campo]}" é obrigatório.'

    if dados["titulo"] and len(dados["titulo"]) > 120:
        erros["titulo"] = "O título deve ter no máximo 120 caracteres."
    if dados["categoria"] and dados["categoria"] not in CATEGORIAS:
        erros["categoria"] = "Categoria inválida. Escolha uma das opções exibidas."
    if dados["gravidade"] and dados["gravidade"] not in GRAVIDADES:
        erros["gravidade"] = "Gravidade inválida. Use baixa, média ou alta."
    return erros


def criar_app(caminho_banco=None):
    """Monta a aplicação; caminho alternativo permite testar sem tocar no banco real."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SOS_SECRET_KEY") or secrets.token_hex(32)
    app.config["DATABASE"] = str(caminho_banco or CAMINHO_BANCO)
    inicializar_banco(app.config["DATABASE"])

    def todos_os_problemas():
        with closing(conectar(app.config["DATABASE"])) as conexao:
            return conexao.execute(
                "SELECT * FROM problemas ORDER BY id DESC"
            ).fetchall()

    def obter_problema(identificador):
        with closing(conectar(app.config["DATABASE"])) as conexao:
            return conexao.execute(
                "SELECT * FROM problemas WHERE id = ?", (identificador,)
            ).fetchone()

    @app.get("/")
    def listar():
        return render_template(
            "index.html", problemas=todos_os_problemas(), dados={}, erros={}
        )

    @app.post("/problemas")
    def cadastrar():
        dados = dados_do_formulario(request.form)
        erros = validar(dados)
        if erros:
            return (
                render_template(
                    "index.html", problemas=todos_os_problemas(), dados=dados, erros=erros
                ),
                400,
            )

        with closing(conectar(app.config["DATABASE"])) as conexao:
            conexao.execute(
                """INSERT INTO problemas
                   (titulo, sistema, categoria, gravidade, descricao)
                   VALUES (?, ?, ?, ?, ?)""",
                tuple(dados[campo] for campo in CAMPOS),
            )
            conexao.commit()
        flash("Problema registrado com sucesso.", "sucesso")
        return redirect(url_for("listar"))

    @app.route("/problemas/<int:identificador>/editar", methods=["GET", "POST"])
    def editar(identificador):
        problema = obter_problema(identificador)
        if problema is None:
            abort(404, description=f"O problema #{identificador} não foi encontrado.")

        if request.method == "GET":
            return render_template("editar.html", problema=problema, dados=dict(problema), erros={})

        # O sistema é exibido na edição, mas não faz parte dos campos alteráveis.
        dados = dados_do_formulario(request.form)
        dados["sistema"] = problema["sistema"].strip()
        erros = validar(dados)
        if erros:
            return render_template("editar.html", problema=problema, dados=dados, erros=erros), 400

        with closing(conectar(app.config["DATABASE"])) as conexao:
            conexao.execute(
                """UPDATE problemas
                   SET titulo = ?, categoria = ?, gravidade = ?, descricao = ?
                   WHERE id = ?""",
                (
                    dados["titulo"], dados["categoria"], dados["gravidade"],
                    dados["descricao"], identificador,
                ),
            )
            conexao.commit()
        flash("Problema atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar"))

    @app.post("/problemas/<int:identificador>/excluir")
    def excluir(identificador):
        with closing(conectar(app.config["DATABASE"])) as conexao:
            cursor = conexao.execute(
                "DELETE FROM problemas WHERE id = ?", (identificador,)
            )
            conexao.commit()
            removido = cursor.rowcount > 0
        if not removido:
            abort(404, description=f"O problema #{identificador} não foi encontrado.")
        flash("Problema excluído com sucesso.", "sucesso")
        return redirect(url_for("listar"))

    @app.errorhandler(404)
    def nao_encontrado(erro):
        return render_template("404.html", mensagem=erro.description), 404

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
