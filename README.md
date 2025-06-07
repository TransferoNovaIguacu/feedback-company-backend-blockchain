## 📘 Transfero Academy
## 🌐 Plataforma de Feedbacks com Recompensas em Tokens


> Este repositório contém o código-fonte do backend (Django REST) da plataforma de feedback. A branch `dev` é usada para desenvolvimento contínuo.

---

## 📌 Sobre o Projeto

Esta plataforma conecta **empresas** que desejam receber feedbacks qualificados com **usuários comuns**, que são recompensados em **tokens** ao completarem missões ou responderem questionários.

Além disso, há **analistas** que avaliam os feedbacks, e um **administrador** que gerencia planos, contratos e transações da plataforma.

Os tokens simulam uma estrutura blockchain (com suporte real a carteiras via BNB Chain ou Polygon na produção e ETH-Sepolia no desenvolvimento).

---

## 🚀 Tecnologias Principais

- **Backend**: Django + Django REST Framework  
- **Blockchain**: Integração com Smart Contracts (Solidity)  
- **Banco de dados**: PostgreSQL (produção), SQLite (dev)  
- **Autenticação**: JWT  
- **Frontend (em outro repositório)**: React  

---

## 🧑‍💻 Requisitos para rodar localmente

Antes de iniciar, instale os seguintes itens:

- Python 3.10+
- pip
- [Poetry](https://python-poetry.org/) (opcional) ou Venv
- Git

---

## 📝 Como Contribuir para o Repositório

Este tutorial descreve o fluxo ideal de trabalho para contribuir com o projeto. Siga as etapas abaixo para garantir que suas alterações sejam integradas ao repositório principal de forma eficiente.

## ⚙️ Instalação e Setup Local

### 1. Faça o Fork do Repositório
Acesse o repositório de desenvolvimento: **[Repositório de desenvolvimento](https://github.com/TransferoNovaIguacu/feedback-company-backend/tree/dev)**

Clique no botão **Fork** no canto superior direito. Isso irá criar uma cópia do repositório na sua conta do GitHub.

### 2. Clone o Repositório Forkado
Depois de fazer o fork, clone o repositório para o seu computador utilizando o link do seu fork:

```bash
git clone --branch dev --single-branch https://github.com/SEU-USUARIO/feedback-company-backend.git
```

### 3. Configure o Ambiente Local

Crie e ative um ambiente virtual:

Com `venv`:

```bash
python -m venv venv
venv\Scripts\activate
```

Ou se preferir usar o `poetry`:

```bash
poetry install
poetry shell
```

### 4. Instale as Dependências do Projeto

```bash
pip install -r requirements-dev.txt
```

### 5. Crie o Arquivo `.env`

Na pasta raiz do projeto, crie um arquivo `.env` com as seguintes variáveis de ambiente:

```env
SECRET_KEY=teste123
DEBUG=True
ALLOWED_HOSTS= 127.0.0.1
```

### 6. Execute as Migrações e Crie um Superusuário

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Rode o Servidor Local

```bash
python manage.py runserver
```

---

## 🧠 Planejamento e Documentação

Consulte a pasta `/docs` para mais informações, como:

- 📄 Requisitos funcionais e não funcionais
- 🧭 Regras de negócio e fluxos do sistema
- 📊 Diagramas de classes UML
- 🗂️ Backlog de Tarefas

---

## 👥 Fluxo de Contribuição

## *Apenas realize as etapas abaixo após realizar o fork, clone, e instalação do projeto.*

### 1. Sincronizando seu Repositório com o Principal

Adicione o repositório principal como `upstream`:

```bash
git remote add upstream https://github.com/TransferoNovaIguacu/feedback-company-backend.git
```

Atualize seu repositório local:

```bash
git fetch upstream
git checkout dev
git merge upstream/dev
```

### 2. Criação de Branch

Crie uma nova branch:

```bash
git checkout -b <tipo>/descricao-da-tarefa
```

Exemplo:

```bash
git checkout -b feature/login-system
```

> 💡 Visite [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/) para entender o padrão de nomenclatura.

### 3. Fazendo Alterações e Commitando

```bash
git add .
git commit -m "feat: add user login system"
```

### 4. Subindo as Alterações para o Seu Repositório Forkado

```bash
git push origin <nome-da-branch>
```

### 5. Criando o Pull Request

- Acesse seu repositório no GitHub
- Selecione a branch que você acabou de enviar
- Clique em **Compare & pull request**
- Descreva as mudanças e clique em **Create pull request**

> ⚠️ Certifique-se de enviar o Pull Request para a branch `dev` do repositório principal.

### 6. Aguardando Revisão

Espere a revisão e aprovação do seu Pull Request. Caso haja feedbacks, faça os ajustes e envie novamente.

---

## 🚧 Fluxo Completo de Contribuição

- Fork e Clone do Repositório Principal
- Sincronização com o Repositório Principal (`upstream`)
- Criação de Branch para Tarefa
- Alterações, Commit e Push
- Criação do Pull Request
- Aguardando Revisão e Aprovação

