"""Testes dos contratos principais da atividade, usando apenas dados fictícios."""

from contextlib import closing
from html import unescape
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app import criar_app, inicializar_banco


EXEMPLO = {
    "titulo": "App Banco — botão invisível",
    "sistema": "App Banco (fictício)",
    "categoria": "acessibilidade",
    "gravidade": "alta",
    "descricao": "O botão de confirmação tem pouco contraste com o fundo.",
}


class SOSUsabilidadeTestes(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.banco = Path(self.pasta.name) / "problemas.db"
        self.app = criar_app(self.banco)
        self.app.testing = True
        self.cliente = self.app.test_client()

    def tearDown(self):
        self.pasta.cleanup()

    def registros(self):
        with closing(sqlite3.connect(self.banco)) as conexao:
            return conexao.execute("SELECT * FROM problemas ORDER BY id DESC").fetchall()

    def cadastrar(self, **alteracoes):
        return self.cliente.post("/problemas", data={**EXEMPLO, **alteracoes})

    def test_t1_t2_banco_idempotente_e_pagina_vazia(self):
        inicializar_banco(self.banco)
        inicializar_banco(self.banco)
        self.assertTrue(self.banco.exists())
        self.assertEqual(self.registros(), [])
        resposta = self.cliente.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Nenhum problema registrado", resposta.get_data(as_text=True))

    def test_t3_a_t5_e_limite_do_titulo(self):
        for alteracoes, mensagem in (
            ({"titulo": "   "}, 'O campo "Título" é obrigatório.'),
            ({"categoria": "interface"}, "Categoria inválida."),
            ({"gravidade": "critica"}, "Gravidade inválida."),
            ({"titulo": "a" * 121}, "no máximo 120 caracteres"),
        ):
            with self.subTest(alteracoes=alteracoes):
                resposta = self.cadastrar(**alteracoes)
                self.assertEqual(resposta.status_code, 400)
                self.assertIn(mensagem, unescape(resposta.get_data(as_text=True)))
                self.assertEqual(self.registros(), [])

    def test_t6_a_t9_cadastro_listagem_aspas_e_reinicio(self):
        resposta = self.cadastrar(titulo="  App Banco — botão invisível  ")
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.headers["Location"], "/")
        self.assertEqual(self.registros()[0][1], EXEMPLO["titulo"])

        pagina = self.cliente.get("/").get_data(as_text=True)
        self.assertIn(EXEMPLO["titulo"], pagina)
        self.assertIn(EXEMPLO["sistema"], pagina)
        self.assertIn("Acessibilidade", pagina)
        self.assertIn("Alta", pagina)
        self.assertEqual(len(self.registros()), 1)  # Atualizar GET não repete o POST.

        self.assertEqual(self.cadastrar(titulo="O'Connor: erro no menu").status_code, 302)
        self.assertEqual(len(self.registros()), 2)
        # Nova instância lê o mesmo arquivo, como após parar e iniciar o Flask.
        novo_cliente = criar_app(self.banco).test_client()
        pagina_reiniciada = novo_cliente.get("/").get_data(as_text=True)
        self.assertIn(EXEMPLO["titulo"], pagina_reiniciada)
        self.assertIn("O&#39;Connor", pagina_reiniciada)
        self.assertLess(pagina_reiniciada.find("O&#39;Connor"), pagina_reiniciada.find(EXEMPLO["titulo"]))

    def test_t10_a_t12_edicao_e_persistencia(self):
        self.cadastrar()
        formulario = self.cliente.get("/problemas/1/editar")
        self.assertEqual(formulario.status_code, 200)
        self.assertIn(EXEMPLO["titulo"], formulario.get_data(as_text=True))

        resposta = self.cliente.post(
            "/problemas/1/editar",
            data={**EXEMPLO, "gravidade": "media", "titulo": "  Botão difícil de ver  "},
        )
        self.assertEqual(resposta.status_code, 302)
        with closing(sqlite3.connect(self.banco)) as conexao:
            linha = conexao.execute("SELECT titulo, sistema, gravidade FROM problemas WHERE id = ?", (1,)).fetchone()
        self.assertEqual(linha, ("Botão difícil de ver", EXEMPLO["sistema"], "media"))

        novo_cliente = criar_app(self.banco).test_client()
        pagina = novo_cliente.get("/").get_data(as_text=True)
        self.assertIn("Botão difícil de ver", pagina)
        self.assertIn("Média", pagina)

    def test_edicao_invalida_nao_altera_o_banco(self):
        self.cadastrar()
        resposta = self.cliente.post(
            "/problemas/1/editar", data={**EXEMPLO, "categoria": "desconhecida"}
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("Categoria inválida", resposta.get_data(as_text=True))
        self.assertEqual(self.registros()[0][3], EXEMPLO["categoria"])

    def test_t13_a_t15_exclusao_id_inexistente_e_persistencia(self):
        self.cadastrar()
        self.assertEqual(self.cliente.post("/problemas/1/excluir").status_code, 302)
        self.assertEqual(self.registros(), [])
        resposta = self.cliente.post("/problemas/999/excluir")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("não foi encontrado", resposta.get_data(as_text=True))
        self.assertEqual(self.cliente.get("/problemas/999/editar").status_code, 404)
        novo_cliente = criar_app(self.banco).test_client()
        self.assertIn("Nenhum problema registrado", novo_cliente.get("/").get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
