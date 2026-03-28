# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Refatoração do perfil "Estabelecimento" com separação de dados fixos (perfil) e variáveis (oferta), limpeza de campos duplicados, Hub de Mídia funcional e automação de links do Instagram.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`, `financial_logs`, `client_tokens`, `client_credits`
- **Endpoints**:
  - `POST/GET/PUT /api/establishments/{id}` - Gerenciamento do estabelecimento
  - `GET /api/establishments/me/financial` - Saldo para saque e logs financeiros
  - `POST/GET /api/offers` - Gerenciamento de ofertas
  - `GET /api/offers/code/{offer_code}` - Busca por código da oferta
  - `GET /api/referral/share-link` - Link dinâmico de indicação
  - `POST /api/qr/generate` - Geração de QR com tokens OU créditos
  - `POST /api/qr/validate` - Validação com fluxo de créditos
  - `POST /api/auth/email-login` - Login via email (modo teste)

### Frontend (Expo React Native Web)
- `/` - Tela de Seleção (Cliente/Estabelecimento)
- `/login` - Login com Google ou Email
- `/(tabs)` - Área do Cliente (Ofertas, QR, Carteira, Ajuda, Perfil)
- `/offer/[id]` - Detalhes da oferta + QRModal com tokens/créditos
- `/establishment/dashboard` - Dashboard com Créditos Recebidos (Saldo para Saque)
- `/establishment/validate` - Validação QR com confirmação de créditos

## Implementation Log
- **25/03/2026**: Implementação completa da refatoração inicial
- **26/03/2026**: Restauração do código do GitHub + Mock Auth
- **28/03/2026**: Bug Fix - Botão "Publicar Oferta" (modo simulação)
- **28/03/2026**: Código Identificador de Ofertas (OFF-XXXXXX)
- **28/03/2026**: CRITICAL FIX - Referral Links & Financial Dashboard
- **28/03/2026**: **QR Code com Créditos - Fluxo Financeiro Completo**
  - QRModal mostra saldo de Tokens E Créditos
  - Cliente pode escolher pagar com Token (1) ou Créditos (R$)
  - Endpoint /api/qr/generate aceita `use_credits` opcional
  - Validação: Verifica se tem tokens OU créditos suficientes
  - Logs financeiros atualizados para tracking

## Core Requirements (Implementados)
- [x] MODO SIMULAÇÃO: Criação de ofertas sem verificação de tokens
- [x] CÓDIGO DA OFERTA: Formato OFF-XXXXXX para rastreamento fácil
- [x] LINKS DE REFERÊNCIA DINÂMICOS: Não expiram mais
- [x] CRÉDITOS RECEBIDOS: Visível no dashboard do estabelecimento
- [x] FLUXO DE CRÉDITOS: Dedução do cliente → Adição ao estabelecimento
- [x] AUDITORIA: Logs financeiros em `financial_logs`
- [x] **QR CODE COM OPÇÕES**: Cliente escolhe pagar com Token ou Créditos

## Tech Stack
- Backend: FastAPI, Motor (async MongoDB), Pydantic
- Frontend: Expo (React Native Web), Expo Router, Zustand
- AI: Gemini 3.1 Flash Image Preview (via Emergent LLM Key)

## Backlog
### P0 (Crítico) - RESOLVIDOS
- [x] Bug Fix: Botão "Publicar Oferta"
- [x] Código identificador de ofertas
- [x] Links de referência expirando
- [x] Dashboard financeiro do estabelecimento
- [x] QR Code com opção de usar créditos

### P1 (Alta Prioridade)
- [ ] Edição de ofertas existentes
- [ ] Busca Digital no Media Hub

### P2 (Média Prioridade)
- [ ] Restaurar autenticação Google OAuth
- [ ] Filtro de ofertas por cidade/bairro

## Next Tasks
1. Testar fluxo completo de QR com créditos no frontend
2. Implementar endpoint para adicionar créditos de teste
3. Adicionar histórico de transações do cliente
