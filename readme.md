# Documentação da aplicação de investimentos

Esta documentação abrange a arquitetura, modelagem do banco de dados, e componentes da aplicação de investimentos, destinada à análise e previsão do mercado financeiro.

## Arquitetura Geral

A aplicação é dividida em três segmentos principais: um frontend web, um backend API em Node.js, e um serviço de machine learning em Python para treinamento e previsão de modelos. MongoDB é utilizado para armazenar dados de usuários, ativos, previsões, e modelos.

### Componentes da Aplicação

Component Diagram:

![Component Diagram](machine_learning/src/doc/component_diagram.png)

Solution Architecture Diagram:

![Solution Architecture](machine_learning/src/doc/sol-arch.png)

## Modelagem do Banco de Dados

A modelagem do banco de dados é projetada para suportar eficientemente o armazenamento e a recuperação de séries temporais de dados de mercado, previsões, modelos de machine learning, e relatórios gerados.

### Coleções

- **Ativos (Assets):** Detalhes sobre ações e criptomoedas.
- **Séries Temporais (TimeSeries):** Dados históricos de preços e volumes.
- **Previsões (Forecasts):** Resultados das previsões dos modelos.
- **Modelos (Models):** Informações dos modelos de machine learning.
- **Relatórios (Reports):** Dados sobre relatórios gerados.
- **Configurações (Configurations):** Configurações gerais da aplicação.

**1 - Ativos (Assets):**

Identificador único (ID)
Tipo (Ação, Criptomoeda)
Ticker
Nome
Setor/Segmento (para ações)
Dados Históricos (referência para coleção TimeSeries)

**2 - TimeSeries (TimeSeries):**

Identificador único do ativo (referência para Assets)
Data
Preço de Abertura
Preço de Fechamento
Alta
Baixa
Volume

**3 - Previsões (Forecasts):**

Identificador único do ativo (referência para Assets)
Modelo (ID do modelo utilizado)
Período da Previsão
Dados da Previsão (podem ser armazenados como um documento aninhado contendo datas e valores previstos)

**4 - Modelos (Models):**

Identificador único (ID)
Tipo (ex: Prophet)
Parâmetros do Modelo
Data de Treinamento
Métricas de Desempenho (ex: MAPE)
Estado (ativo, inativo)

**5 - Relatórios (Reports):**

Identificador único do ativo (referência para Assets)
Tipo de Relatório (análise técnica, previsão, etc.)
Caminho do Arquivo
Data de Geração

**6 - Configurações (Configurations):**

Chave de Configuração
Valor

## Descrição da Aplicação

### Frontend

Interface web que permite aos usuários visualizar dados históricos, previsões de mercado, gerar e visualizar relatórios, e interagir com o sistema de previsões.

### Backend API

Desenvolvido em Node.js, serve como a camada intermediária entre o frontend, o serviço de machine learning, e o banco de dados. Gerencia autenticações, operações CRUD, e invoca o serviço de machine learning.

### Serviço de Machine Learning

Implementado em Python, utiliza bibliotecas como Prophet, NumPy, e Scikit-Learn para treinar modelos e realizar previsões, que são armazenadas no MongoDB.

### Funcionamento

**1 - Treinamento de Modelos:** Realizado pelo serviço de Python, utilizando dados históricos.
**2 - Geração de Previsões:** Modelos treinados geram previsões, armazenadas no banco de dados.
**3 - Visualização e Análise:** Usuários acessam dados históricos, previsões, e relatórios através do frontend.
**4 - Gestão de Dados:** Adição, atualização ou remoção de ativos pelo usuário, além de solicitações para novos treinamentos e previsões.

### Documentação Técnica

**- Python:** Versão compatível com as bibliotecas utilizadas (>=3.8 e <=3.9).
**- Dependências:** Inclui Prophet, Pandas, e outras bibliotecas para análise de dados.
**- Docker:** Utilizado para containerizar o serviço de Python, facilitando desenvolvimento e deployment.

## Executando a API Python

Para executar a API Python da aplicação de investimentos, siga os passos detalhados abaixo. Essas instruções pressupõem que você já tem o Docker instalado em seu ambiente, uma vez que a aplicação utiliza Docker para facilitar a configuração e execução do ambiente de desenvolvimento.

### Pré-requisitos:

**1 - Docker:** Certifique-se de que o Docker está instalado e funcionando em sua máquina. Visite a página oficial do Docker para instruções de instalação.
**2 - Código Fonte:** Clone o repositório da aplicação de investimentos para sua máquina local, caso ainda não o tenha feito.

### Passos para Execução:

Abra o Terminal ou Prompt de Comando: Navegue até o diretório onde o projeto foi clonado.

### Construção da Imagem Docker:

Utilize o seguinte comando para construir a imagem Docker da aplicação, baseando-se no Dockerfile presente na raiz do projeto:

`docker-compose build`

Este comando irá ler as configurações do docker-compose.yml e do Dockerfile, instalando as dependências necessárias e preparando o ambiente para execução.

### Executando a Aplicação:

Após a construção da imagem, utilize o seguinte comando para iniciar a aplicação:

`docker-compose up`
Este comando inicia os serviços definidos no arquivo docker-compose.yml, incluindo a API Python.

### Acesso à Aplicação:

Com a aplicação rodando, você pode acessá-la utilizando o navegador ou um cliente de API (como Postman) para fazer requisições HTTP para o endereço configurado. Se tudo estiver configurado corretamente, a API Python estará escutando na porta 5678, como especificado no docker-compose.yml.

### Desenvolvimento Interativo:

A aplicação é configurada para permitir o desenvolvimento interativo com o suporte do debugpy. Isso significa que você pode anexar um depurador ao processo em execução dentro do container para depuração em tempo real.

### Dicas Adicionais:

**- Logs:** Para visualizar os logs da aplicação em tempo real, mantenha o terminal aberto após executar o comando docker-compose up. Os logs serão úteis para depuração e monitoramento da aplicação.

**- Parando a Aplicação:** Para parar a aplicação, você pode usar o comando Ctrl+C no terminal onde ela está rodando. Para parar e remover todos os containers criados pelo docker-compose, utilize:

`docker-compose down`

### Atualizações:

Se você fizer alterações no código da aplicação ou nas dependências, pode ser necessário reconstruir a imagem Docker. Use docker-compose build para reconstruir a imagem e docker-compose up para reiniciar a aplicação.
