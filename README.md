# SOS Usabilidade

Aplicação local em Flask e SQLite para registrar problemas fictícios de interface. Implementa a [atividade de 28/09](https://github.com/elzobrito/usjt/blob/main/usabilidade-web-mobile-jogos/2026-2/atividades/2809/atividade-python-sqlite.md) e usa o [wireframe fornecido](https://github.com/elzobrito/usjt/blob/main/usabilidade-web-mobile-jogos/2026-2/atividades/2809/wireframe-sos-usabilidade.html) como referência.

## Executar no Windows (PowerShell)

Na pasta `sos-usabilidade`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abra <http://127.0.0.1:5000/>. Encerre com `Ctrl+C`. O arquivo `problemas.db` nasce automaticamente ao iniciar o app e fica nesta pasta. Depois de reiniciar, os registros continuam no banco. Use somente exemplos inventados.

Para executar os testes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Decisões de implementação

1. **Conexões:** cada operação abre uma conexão curta usando `closing(...)`, e ela é fechada inclusive se ocorrer uma exceção. Escritas recebem `commit()` antes do redirecionamento. A inicialização usa `CREATE TABLE IF NOT EXISTS`, portanto pode ser repetida.
2. **Validação:** categoria e gravidade são validadas em Python, junto com campos obrigatórios e limite de 120 caracteres do título. Assim, a resposta pode mostrar uma mensagem específica sem depender do texto interno de uma exceção SQLite. Todos os campos recebidos passam por `strip()` antes da validação.
3. **ID inexistente:** edição e exclusão retornam uma página 404 com texto explicativo e link de volta. O status HTTP continua correto e a pessoa sabe como prosseguir.
4. **Feedback:** após cadastro, edição e exclusão, `flash()` mostra o sucesso na listagem. Um formulário inválido é renderizado com status 400, mensagens textuais e os valores preservados. Cadastro e edição seguem o padrão POST–redirect–GET após sucesso.
5. **Confirmação da exclusão:** o botão “Excluir” abre uma confirmação inline com HTML `<details>`. A remoção só acontece ao clicar “Sim, excluir”, que envia POST. Isso evita exclusão acidental sem exigir JavaScript.
6. **Rota de edição:** GET e POST ficam na mesma função porque compartilham a busca do registro. O campo `sistema` é exibido, mas não é alterado pela edição, conforme o contrato da atividade.

As consultas e escritas usam parâmetros `?` para valores dinâmicos. A lista usa `ORDER BY id DESC`, que mantém os registros mais recentes no topo mesmo quando são criados no mesmo segundo. O servidor escuta apenas em `127.0.0.1`.

## Estrutura

- `app.py`: rotas, validação e acesso ao SQLite.
- `templates/`: páginas HTML e formulário compartilhado.
- `static/style.css`: visual e adaptação para telas menores.
- `tests/test_app.py`: testes dos contratos de aceitação com banco temporário.
- `TESTES.md`: resultados e roteiro para revisão manual.

O banco e o ambiente virtual estão no `.gitignore` e não devem ser entregues como parte do código.
