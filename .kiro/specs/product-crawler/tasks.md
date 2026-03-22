# Plano de Implementação: Product Crawler

## Visão Geral

Implementação incremental da aplicação web de extração de dados de produtos. Cada tarefa constrói sobre a anterior, começando pela estrutura do projeto e interfaces, passando pela lógica de validação e crawler, até a integração final com templates e estilos.

## Tarefas

- [x] 0. Criar e ativar ambiente virtual Python e instalar dependências
  - [x] 0.1 Criar o ambiente virtual: `python -m venv venv`
  - [x] 0.2 Ativar o ambiente virtual:
    - No macOS/Linux: `source venv/bin/activate`
    - No Windows (cmd): `venv\Scripts\activate`
    - No Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
  - [x] 0.3 Instalar dependências: `pip install flask playwright pytest hypothesis`
  - [x] 0.4 Instalar navegadores do Playwright: `playwright install`

- [x] 1. Criar estrutura do projeto e módulo de validação
## Tarefas

- [ ] 1. Criar estrutura do projeto e módulo de validação
  - [x] 1.1 Criar `app.py` com a aplicação Flask, rota GET `/` renderizando `index.html`, e a função `validate_url(url)` que retorna `(bool, str)`
    - Configurar logging com formato `%(asctime)s - %(levelname)s - %(message)s`
    - A função `validate_url` deve rejeitar URLs vazias com "URL é obrigatória" e URLs sem prefixo http/https com "URL inválida"
    - _Requisitos: 1.1, 2.1, 2.2, 2.3, 7.1, 9.1, 10.1, 10.2_

  - [x]* 1.2 Escrever teste de propriedade para validação de URL
    - **Propriedade 1: Validação de URL é consistente com prefixo HTTP/HTTPS**
    - Usar `hypothesis` para gerar strings aleatórias e verificar que `validate_url` retorna válido ⟺ string não vazia e começa com `http://` ou `https://`
    - Mínimo 100 iterações
    - **Valida: Requisitos 2.1, 2.2, 2.3**

  - [x]* 1.3 Escrever testes unitários para `validate_url` e rota GET `/`
    - Testar URL vazia, URL sem protocolo, URL com http://, URL com https://
    - Testar que GET `/` retorna status 200 e contém o formulário
    - _Requisitos: 2.1, 2.2, 2.3, 7.1_

- [x] 2. Implementar o módulo crawler com Playwright
  - [x] 2.1 Criar `crawler.py` com a função `get_product_data(url)` e constantes de seletores
    - Definir `TIMEOUT_MS = 30000` e listas de seletores para título, preço e descrição
    - Implementar abertura do navegador Playwright headless, navegação com timeout, aguardar carregamento do DOM
    - Implementar navegação simulada com scroll e delays
    - Extrair dados usando seletores múltiplos (CSS/XPath), retornando string vazia para campos não encontrados
    - Gerenciar ciclo de vida do navegador (abrir e fechar) dentro da função
    - Implementar tratamento de erros: `TimeoutError` → mensagem de timeout, erro de conexão → mensagem de conexão, exceção genérica → log + mensagem genérica
    - Registrar logs de início, sucesso e erro da extração
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 6.1, 6.2, 6.3, 9.1, 9.2, 9.3, 10.1, 10.2_

  - [x]* 2.2 Escrever teste de propriedade para estrutura do Dados_Produto
    - **Propriedade 2: Estrutura do Dados_Produto é consistente**
    - Gerar dicionários com chaves `title`, `price`, `description` e valores string, verificar que contêm exatamente as chaves esperadas com valores do tipo `str`
    - **Valida: Requisitos 4.4, 4.5**

  - [x]* 2.3 Escrever teste de propriedade para round-trip JSON do Dados_Produto
    - **Propriedade 3: Round-trip de serialização JSON do Dados_Produto**
    - Gerar dicionários com chaves `title`, `price`, `description` e valores string aleatórios, serializar com `json.dumps` e deserializar com `json.loads`, verificar igualdade
    - **Valida: Requisito 5.3**

- [x] 3. Checkpoint — Verificar módulos base
  - Garantir que todos os testes passam, perguntar ao usuário se há dúvidas.

- [x] 4. Implementar rota POST /scrape e templates HTML
  - [x] 4.1 Adicionar rota POST `/scrape` em `app.py`
    - Receber URL do formulário, validar com `validate_url`, chamar `get_product_data` se válida
    - Renderizar `index.html` com erro se URL inválida
    - Renderizar `result.html` com dados do produto ou mensagem de erro do crawler
    - Registrar logs conforme requisitos
    - _Requisitos: 2.1, 2.2, 2.3, 6.4, 7.2, 7.3, 9.1, 9.2, 9.3_

  - [x] 4.2 Criar `templates/index.html`
    - Formulário com campo `<input name="url">` e botão "Buscar produto"
    - Submissão via POST para `/scrape`
    - Exibição condicional de mensagem de erro via Jinja2 `{{ error }}`
    - Incluir link para CSS estático
    - _Requisitos: 1.1, 1.2, 1.3_

  - [x] 4.3 Criar `templates/result.html`
    - Exibir título, preço e descrição do produto de forma formatada
    - Exibir mensagem de erro quando presente
    - Incluir link "Voltar" para `/`
    - Incluir link para CSS estático
    - _Requisitos: 6.4, 8.1, 8.2, 8.3_

  - [x]* 4.4 Escrever teste de propriedade para exibição de erros na página de resultado
    - **Propriedade 4: Mensagens de erro são exibidas na página de resultado**
    - Gerar strings de erro aleatórias, renderizar `result.html` com o erro, verificar que o HTML contém a mensagem
    - **Valida: Requisito 6.4**

  - [x]* 4.5 Escrever teste de propriedade para exibição de dados na página de resultado
    - **Propriedade 5: Dados do produto são exibidos na página de resultado**
    - Gerar `Dados_Produto` com valores aleatórios não vazios, renderizar `result.html`, verificar que o HTML contém título, preço e descrição
    - **Valida: Requisito 8.1**

  - [x]* 4.6 Escrever testes unitários para rota POST `/scrape`
    - Testar POST com URL inválida retorna `index.html` com erro
    - Testar POST com URL válida (mock do crawler) retorna `result.html` com dados
    - Testar que `result.html` contém link de retorno para `/`
    - _Requisitos: 7.2, 7.3, 8.2_

- [x] 5. Criar estilos CSS
  - [x] 5.1 Criar `static/style.css`
    - Estilos para layout limpo e legível: centralização, tipografia, espaçamento do formulário, formatação dos dados do produto
    - _Requisitos: 1.3, 8.3_

- [x] 6. Checkpoint final — Garantir integração completa
  - Garantir que todos os testes passam, perguntar ao usuário se há dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude
- Testes unitários validam exemplos específicos e edge cases
