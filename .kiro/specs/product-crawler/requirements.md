# Documento de Requisitos

## Introdução

Aplicação web para extração de dados de produtos a partir de URLs fornecidas pelo usuário. A aplicação utiliza Flask como framework web e Playwright para simular navegação humana em páginas de produtos, extraindo título, preço e descrição. Os dados extraídos são exibidos em uma página HTML formatada.

## Glossário

- **Aplicação**: Sistema web Flask que serve a interface do usuário e coordena a execução do crawler
- **Crawler**: Módulo Python que utiliza Playwright para abrir páginas web, simular navegação humana e extrair dados de produtos
- **Produto**: Entidade representada por título, preço e descrição, extraída de uma página web
- **URL_Produto**: Endereço web válido (HTTP ou HTTPS) que aponta para uma página de produto
- **Formulário**: Interface HTML onde o usuário insere a URL do produto e submete a requisição
- **Dados_Produto**: Dicionário Python com as chaves "title", "price" e "description"
- **Navegação_Simulada**: Conjunto de ações do Playwright que imitam comportamento humano, incluindo delays e scroll na página
- **Página_Resultado**: Página HTML que exibe os dados extraídos do produto de forma formatada

## Requisitos

### Requisito 1: Página Inicial com Formulário

**User Story:** Como um usuário, eu quero acessar uma página inicial com um formulário de entrada, para que eu possa inserir a URL de um produto e iniciar a extração de dados.

#### Critérios de Aceitação

1. WHEN o usuário acessa a rota raiz (/), THE Aplicação SHALL renderizar a página inicial contendo o título da aplicação, um campo de input para URL e um botão "Buscar produto"
2. THE Formulário SHALL submeter a URL_Produto via método POST para a rota /scrape
3. THE Aplicação SHALL servir arquivos CSS estáticos a partir do diretório /static

### Requisito 2: Validação de URL

**User Story:** Como um usuário, eu quero que a aplicação valide a URL inserida, para que eu receba feedback claro caso a URL seja inválida.

#### Critérios de Aceitação

1. WHEN o usuário submete o Formulário com uma URL_Produto vazia, THE Aplicação SHALL exibir uma mensagem de erro informando que a URL é obrigatória
2. WHEN o usuário submete o Formulário com uma URL_Produto que não inicia com "http://" ou "https://", THE Aplicação SHALL exibir uma mensagem de erro informando que a URL é inválida
3. WHEN o usuário submete o Formulário com uma URL_Produto válida, THE Aplicação SHALL prosseguir com a execução do Crawler

### Requisito 3: Execução do Crawler com Navegação Simulada

**User Story:** Como um usuário, eu quero que o crawler simule navegação humana ao acessar a página do produto, para que os dados sejam carregados corretamente mesmo em páginas com renderização dinâmica.

#### Critérios de Aceitação

1. WHEN a Aplicação recebe uma URL_Produto válida, THE Crawler SHALL abrir um navegador Playwright em modo headless e navegar até a URL_Produto
2. WHEN a página do produto é carregada, THE Crawler SHALL aguardar o carregamento completo do DOM antes de iniciar a extração
3. WHEN a página do produto está carregada, THE Crawler SHALL executar Navegação_Simulada incluindo scroll na página e delays entre ações
4. THE Crawler SHALL configurar um timeout máximo de 30 segundos para o carregamento da página

### Requisito 4: Extração de Dados do Produto

**User Story:** Como um usuário, eu quero que o crawler extraia título, preço e descrição do produto, para que eu possa visualizar essas informações sem navegar manualmente.

#### Critérios de Aceitação

1. WHEN a Navegação_Simulada é concluída, THE Crawler SHALL extrair o título do produto utilizando seletores CSS ou XPath comuns para títulos de produto
2. WHEN a Navegação_Simulada é concluída, THE Crawler SHALL extrair o preço do produto utilizando seletores CSS ou XPath comuns para preços
3. WHEN a Navegação_Simulada é concluída, THE Crawler SHALL extrair a descrição do produto utilizando seletores CSS ou XPath comuns para descrições
4. THE Crawler SHALL retornar os dados extraídos como um Dados_Produto no formato {"title": "", "price": "", "description": ""}
5. WHEN um campo do produto não é encontrado na página, THE Crawler SHALL retornar uma string vazia para o campo correspondente no Dados_Produto

### Requisito 5: Função get_product_data

**User Story:** Como um desenvolvedor, eu quero uma função encapsulada para extração de dados, para que o crawler seja reutilizável e testável.

#### Critérios de Aceitação

1. THE Crawler SHALL expor uma função get_product_data(url) que recebe uma URL_Produto como parâmetro e retorna um Dados_Produto
2. WHEN a função get_product_data é chamada, THE Crawler SHALL gerenciar o ciclo de vida do navegador Playwright (abrir e fechar) dentro da função
3. FOR ALL chamadas válidas à função get_product_data, serializar o Dados_Produto retornado como JSON e deserializar de volta SHALL produzir um dicionário equivalente ao original (propriedade round-trip)

### Requisito 6: Tratamento de Erros do Crawler

**User Story:** Como um usuário, eu quero que a aplicação trate erros de forma adequada, para que eu receba mensagens claras quando algo der errado.

#### Critérios de Aceitação

1. IF o Crawler não consegue acessar a URL_Produto dentro do timeout configurado, THEN THE Crawler SHALL retornar uma mensagem de erro descritiva indicando timeout
2. IF o Crawler encontra um erro de conexão ao acessar a URL_Produto, THEN THE Crawler SHALL retornar uma mensagem de erro descritiva indicando falha de conexão
3. IF ocorre uma exceção inesperada durante a execução do Crawler, THEN THE Crawler SHALL registrar o erro em log e retornar uma mensagem de erro genérica
4. WHEN o Crawler retorna um erro, THE Aplicação SHALL exibir a mensagem de erro na Página_Resultado de forma amigável

### Requisito 7: Rotas do Backend Flask

**User Story:** Como um desenvolvedor, eu quero rotas Flask bem definidas, para que a aplicação tenha uma API clara e organizada.

#### Critérios de Aceitação

1. WHEN uma requisição GET é feita para a rota /, THE Aplicação SHALL renderizar o template index.html com o Formulário
2. WHEN uma requisição POST é feita para a rota /scrape com uma URL_Produto válida, THE Aplicação SHALL executar o Crawler e renderizar o template result.html com os Dados_Produto
3. WHEN uma requisição POST é feita para a rota /scrape com uma URL_Produto inválida, THE Aplicação SHALL renderizar o template index.html com a mensagem de erro de validação

### Requisito 8: Exibição dos Resultados

**User Story:** Como um usuário, eu quero visualizar os dados extraídos de forma clara e organizada, para que eu possa ler facilmente as informações do produto.

#### Critérios de Aceitação

1. WHEN o Crawler retorna Dados_Produto com sucesso, THE Página_Resultado SHALL exibir o título, preço e descrição do produto de forma formatada
2. THE Página_Resultado SHALL incluir um link para retornar à página inicial e realizar uma nova busca
3. THE Página_Resultado SHALL aplicar estilos CSS para apresentar os dados com layout limpo e legível

### Requisito 9: Logging

**User Story:** Como um desenvolvedor, eu quero que a aplicação registre logs das operações, para que eu possa diagnosticar problemas e monitorar o comportamento do sistema.

#### Critérios de Aceitação

1. WHEN o Crawler inicia a extração de uma URL_Produto, THE Aplicação SHALL registrar em log a URL sendo processada
2. WHEN o Crawler conclui a extração com sucesso, THE Aplicação SHALL registrar em log que a extração foi concluída
3. WHEN o Crawler encontra um erro, THE Aplicação SHALL registrar em log o tipo de erro e a mensagem correspondente

### Requisito 10: Estrutura do Projeto

**User Story:** Como um desenvolvedor, eu quero que o projeto siga uma estrutura organizada, para que o código seja fácil de manter e entender.

#### Critérios de Aceitação

1. THE Aplicação SHALL organizar o código em: app.py (backend Flask), crawler.py (módulo do Crawler), templates/index.html (Formulário), templates/result.html (Página_Resultado), static/style.css (estilos)
2. THE Aplicação SHALL manter a lógica do Crawler separada da lógica do backend Flask em módulos distintos
