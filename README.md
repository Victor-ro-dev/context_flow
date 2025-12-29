# SaaS RAG – projeto full‑cycle de arquitetura de software

Este repositório contém um projeto **SaaS full‑cycle** de minha autoria, criado com o objetivo de **consolidar conhecimentos de Arquitetura de Software**, boas práticas de backend, frontend e infraestrutura, em um contexto próximo de produção.

O produto é um **SaaS de RAG (Retrieval-Augmented Generation)**: ele centraliza documentos (PDF, DOCX, CSV, etc.), extrai conhecimento e permite que usuários façam **busca semântica** e recebam respostas contextualizadas, respeitando **limites de plano** e **escopo de organização/usuário**.

---

## 🎯 Objetivos do projeto

- Exercitar **arquitetura enterprise** em um cenário realista (mesmo com poucos clientes).
- Implementar um SaaS **multi-tenant** (usuários + organizações, planos, assinaturas, uso).
- Praticar o ciclo completo (**full-cycle**):
  - modelagem de domínio e banco
  - APIs (autenticação, billing, docs)
  - processamento assíncrono
  - frontend integrado
  - observabilidade e escalabilidade (em etapas futuras).
- Explorar **RAG** com banco vetorial usando `pgvector`.

---

## 🧠 Funcionalidades (MVP)

- **Autenticação & Autorização**
  - Registro e login de usuários.
  - JWT (tokens) emitidos pelo Django, usados pelos serviços.
  - Perfis de acesso e papéis (Admin, Free, Pro, Premium).

- **Multi-tenancy**
  - Usuários individuais e organizações.
  - Escopo de documentos por usuário/organização.
  - Controle de acesso baseado em plano.

- **Planos e Assinaturas**
  - Tabela de `plans` configurável (FREE, PRO, PREMIUM, etc.).
  - `subscriptions` para associar usuários/organizações a planos.
  - Registro de `usage` por período (documentos, queries, armazenamento).

- **Gestão de Documentos**
  - Upload de documentos (PDF, DOCX, CSV etc.).
  - Armazenamento de arquivos no MinIO (S3 compatible).
  - Metadados em PostgreSQL (`documents` e `document_chunks`).
  - Geração de embeddings e armazenamento via `pgvector`.

- **RAG (Retrieval-Augmented Generation)**
  - Consulta semântica sobre os documentos do usuário/organização.
  - Busca vetorial em `document_chunks` com `pgvector`.
  - Integração com LLM (modelo a definir/plugável).

---

## 🏗 Arquitetura

A aplicação é organizada em **três principais componentes**:

### 1. Core API – Django + DRF

Responsável por toda a **regra de negócio**:

- Autenticação, registro e gerenciamento de usuários.
- Gestão de organizações, planos, assinaturas e uso.
- CRUD de documentos e metadados.
- Exposição de APIs REST para o frontend.
- Orquestração de fluxos (ex.: enfileirar processamento de documentos no RabbitMQ).

**Pasta:** `backend-django/`

### 2. RAG Service – FastAPI

Responsável pela parte **intensiva de IA**:

- Processamento de documentos (chunking, limpeza, normalização).
- Geração de embeddings.
- Consulta vetorial (via PostgreSQL + pgvector).
- Montagem das respostas RAG combinando contexto + LLM.
- Exposição de endpoints específicos para RAG, consumidos pelo frontend (e/ou Django).

**Pasta:** `backend-fastapi/`

### 3. Frontend – Next.js

Responsável pela **experiência do usuário**:

- UI para upload e gerenciamento de documentos.
- Interface para realizar perguntas e visualizar respostas.
- Integração com a API de autenticação (JWT em cookies HttpOnly).
- Rotas protegidas com base no estado de login e plano.

**Pasta:** `frontend-nextjs/`

---

## 🧱 Stack de Tecnologias

- **Backend (Core):**  
  - Django  
  - Django REST Framework  
  - JWT (via `djangorestframework-simplejwt` ou similar)

- **Backend (RAG):**  
  - FastAPI  
  - Cliente para LLMs  
  - Integração com PostgreSQL (pgvector)

- **Frontend:**  
  - Next.js  
  - React  
  - TypeScript (planejado)

- **Banco de Dados:**  
  - PostgreSQL  
  - Extensão `pgvector` para embeddings

- **Mensageria & Assíncrono:**  
  - RabbitMQ (message broker)  
  - Celery (task workers)

- **Cache & Sessão:**  
  - Redis (cache + results backend do Celery)

- **Storage de Arquivos:**  
  - MinIO (S3-compatible object storage)

---

## 📂 Estrutura de diretórios (proposta)

```text
.
├─ backend-django/
│  ├─ src/
│  │  ├─ users/
│  │  ├─ organizations/
│  │  ├─ documents/
│  │  ├─ plans/
│  │  ├─ subscriptions/
│  │  └─ usage/
│  └─ ...
│
├─ backend-fastapi/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ rag/
│  │  ├─ models/
│  │  └─ services/
│  └─ ...
│
├─ frontend-nextjs/
│  ├─ app/ ou pages/
│  ├─ components/
│  └─ ...
│
└─ README.md
