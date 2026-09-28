# Verificação da atividade

Os testes automatizados usam um banco temporário com dados fictícios. Resultado em 28/09/2026: **6 testes passaram**, cobrindo os contratos T1–T15 e validações adicionais. Também cadastrei um exemplo fictício pela interface, parei o processo Flask com `Ctrl+C`, iniciei outro processo e confirmei que o registro continuou na listagem. O roteiro abaixo permite repetir a verificação em aula.

| ID | Previsto | Obtido automaticamente |
|---|---|---|
| T1 | Inicializar duas vezes sem erro ou duplicação | Passou |
| T2 | `GET /` com banco vazio retorna página válida | Passou |
| T3 | Título em branco é recusado com texto explicativo | Passou |
| T4 | Categoria inválida é recusada | Passou |
| T5 | Gravidade inválida é recusada | Passou |
| T6 | Cadastro válido redireciona e grava no banco | Passou |
| T7 | A listagem mostra o registro | Passou |
| T8 | Aspas simples no título não quebram a consulta | Passou |
| T9 | Nova instância Flask lê o cadastro anterior | Passou no teste e após parada real do servidor |
| T10 | Edição abre formulário com dados preenchidos | Passou |
| T11 | POST de edição muda a gravidade de alta para média | Passou |
| T12 | Nova instância Flask lê a alteração | Passou; parada real no roteiro manual |
| T13 | POST de exclusão remove o registro | Passou |
| T14 | Exclusão de ID inexistente retorna 404 explicativo | Passou |
| T15 | Nova instância Flask mantém o registro excluído ausente | Passou; parada real no roteiro manual |

## Roteiro manual para a aula

Antes de cada teste manual, registre sua própria previsão na coluna **Previsto**. Depois preencha **Obtido**, **Diagnóstico/correção** se houver divergência e **Reteste**. Para T8, T9, T12 e T15, peça a outra pessoa que execute a revisão cruzada sem ler o código primeiro.

1. Inicie `app.py`, abra <http://127.0.0.1:5000/> e cadastre “App Banco — botão invisível”, usando apenas informações inventadas.
2. Cadastre outro título com aspas, por exemplo `O'Connor — menu confuso`.
3. Anote o que espera ver após parar o servidor; use `Ctrl+C`, inicie `app.py` novamente e atualize a página. Confira os dois registros (T8–T9).
4. Edite o primeiro registro, altere a gravidade de `alta` para `media`, pare e reinicie o servidor. Confira a alteração (T10–T12).
5. Abra “Excluir”, confirme a remoção, tente excluir um ID inexistente acessando `/problemas/999/excluir` via POST (ou use o teste automatizado), pare e reinicie o servidor. Confira que o registro removido não voltou (T13–T15).

| ID | Previsto antes da execução | Obtido | Diagnóstico / correção | Reteste |
|---|---|---|---|---|
| T8 |  |  |  |  |
| T9 |  |  |  |  |
| T12 |  |  |  |  |
| T15 |  |  |  |  |
