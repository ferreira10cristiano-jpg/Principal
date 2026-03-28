# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Plataforma de fidelidade e ofertas para estabelecimentos e clientes. Estabelecimentos criam ofertas com descontos, clientes geram QR Codes (vouchers) para resgatar ofertas, e o sistema rastreia vendas, créditos e comissões de indicação.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`, `vouchers`, `sales_history`, `financial_logs`, `client_tokens`, `client_credits`, `referral_network`, `transactions`
- **Endpoints Principais**:
  - `POST /api/auth/email-login` - Login via email (modo teste)
  - `POST/GET/PUT /api/establishments/{id}` - Gerenciamento do estabelecimento
  - `GET /api/establishments/me/financial` - Saldo para saque
  - `GET /api/establishments/me/sales-history` - Histórico de vendas
  - `POST/GET /api/offers` - Gerenciamento de ofertas
  - `GET /api/offers/code/{offer_code}` - Busca por código da oferta
  - `POST /api/qr/generate` - Geração de voucher QR (deduz 1 token, créditos opcionais)
  - `POST /api/qr/validate` - Validação via code_hash ou backup_code (ITK-XXX)
  - `GET /api/vouchers/my` - Vouchers do cliente (tela "Meus QR")
  - `GET /api/referral/share-link` - Link dinâmico de indicação

### Frontend (Expo React Native Web)
- `/` - Tela de Seleção (Cliente/Estabelecimento)
- `/login` - Login com Email
- `/(tabs)` - Área do Cliente (index, qr, wallet, credits, network, help, profile)
- `/(tabs)/qr` - "Meus QR" - lista vouchers com backup code em destaque
- `/offer/[id]` - Detalhes da oferta + QRModal com tokens/créditos
- `/qr-fullscreen` - QR Code em tela cheia com backup code
- `/establishment/dashboard` - Dashboard com Créditos Recebidos
- `/establishment/offers` - Gerenciamento de ofertas
- `/establishment/validate` - Validação QR com câmera (expo-camera) + input manual

## Implementation Log
- **25/03/2026**: Implementação completa da refatoração inicial
- **26/03/2026**: Restauração do código do GitHub + Mock Auth
- **28/03/2026**: Bug Fix - Botão "Publicar Oferta" (modo simulação)
- **28/03/2026**: Código Identificador de Ofertas (OFF-XXXXXX)
- **28/03/2026**: CRITICAL FIX - Referral Links & Financial Dashboard
- **28/03/2026**: QR Code com Créditos - Fluxo Financeiro Completo
- **28/03/2026**: CRITICAL REFACTOR - Vouchers persistidos, backup codes (ITK-XXX), câmera scanner, sales history
- **28/03/2026**: FIX - MongoDB ObjectId serialization em /api/qr/validate
- **28/03/2026**: FIX - Frontend "Meus QR" agora busca de /vouchers/my com backup code visível

## Core Requirements (Implementados)
- [x] MODO SIMULAÇÃO: Criação de ofertas sem verificação de tokens
- [x] CÓDIGO DA OFERTA: Formato OFF-XXXXXX para rastreamento
- [x] LINKS DE REFERÊNCIA DINÂMICOS
- [x] CRÉDITOS RECEBIDOS: Dashboard do estabelecimento
- [x] FLUXO DE CRÉDITOS: Dedução do cliente -> Adição ao estabelecimento
- [x] AUDITORIA: Logs financeiros em `financial_logs`
- [x] QR CODE COM OPÇÕES: Token (obrigatório) + Créditos (opcional)
- [x] VOUCHERS PERSISTIDOS: Coleção `vouchers` com backup_code (ITK-XXX)
- [x] SALES HISTORY: Registro de vendas com créditos e valor em dinheiro
- [x] VALIDAÇÃO QR: Suporte a code_hash e backup_code
- [x] CÂMERA SCANNER: expo-camera na tela de validação do estabelecimento
- [x] MEUS QR: Tela de vouchers do cliente com backup code em destaque
- [x] QR FULLSCREEN: Tela cheia com backup code visível

## Tech Stack
- Backend: FastAPI, Motor (async MongoDB), Pydantic
- Frontend: Expo (React Native Web), Expo Router, Zustand, expo-camera
- AI: Gemini 3.1 Flash Image Preview (via Emergent LLM Key)

## Backlog

### P1 (Alta Prioridade)
- [ ] Edição de ofertas existentes
- [ ] Busca Digital no Media Hub

### P2 (Média Prioridade)
- [ ] Restaurar autenticação Google OAuth
- [ ] Filtro de ofertas por cidade/bairro
- [ ] Refatorar server.py (>2100 linhas) em FastAPI APIRouters
- [ ] Adicionar histórico de transações do cliente

## Next Tasks
1. Testar fluxo completo de geração e validação de QR no frontend
2. Implementar edição de ofertas existentes
3. Refatorar server.py em módulos
