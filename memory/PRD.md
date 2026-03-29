# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Plataforma de fidelidade e ofertas para estabelecimentos e clientes. Estabelecimentos criam ofertas com descontos, clientes geram QR Codes (vouchers) para resgatar ofertas, e o sistema rastreia vendas, creditos e comissoes de indicacao.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`, `vouchers`, `sales_history`, `financial_logs`, `client_tokens`, `client_credits`, `referral_network`, `transactions`, `token_purchases`, `platform_settings`
- **Endpoints Principais**:
  - `POST /api/auth/email-login` - Login via email
  - `POST /api/qr/generate` - Gera voucher QR
  - `POST /api/qr/validate` - Step 1: Preview do voucher
  - `POST /api/qr/confirm` - Step 2: Confirma recebimento
  - `GET /api/vouchers/my` - Vouchers do cliente
  - `POST /api/vouchers/{id}/cancel` - Cancela e devolve creditos
  - `GET /api/establishments/me/sales-history` - Historico de vendas
  - `GET /api/admin/stats` - Stats reais do MongoDB
  - `GET /api/admin/search-voucher?code=ITK-XXX` - Auditoria de voucher
  - `GET /api/admin/financial` - Receita bruta, liquida, saldo a liquidar
  - `GET /api/admin/settings` - Configuracoes globais (comissao %)
  - `PUT /api/admin/settings` - Atualizar comissao global
  - `GET /api/admin/transactions` - Transacoes admin

### Frontend (Expo React Native Web)
- **QRModal**: displayMode state (generate/loading/result)
- **QR Fullscreen**: Valor Original, Creditos, Valor Final
- **Meus QR**: Cards com breakdown de preco, backup code, cancelar
- **Validate (Estabelecimento)**: html5-qrcode scanner + 2 etapas
- **Admin Dashboard**: Fundo branco, 3 abas (Visao Geral, Financeiro, Usuarios)

## Implementation Log
- **25-28/03/2026**: MVP completo com ofertas, QR codes, validacao
- **28/03/2026**: CRITICAL REFACTOR - Vouchers persistidos, backup codes, camera scanner
- **28/03/2026**: URGENT REFACTOR - Deducao imediata de creditos, cancelamento com devolucao
- **28/03/2026**: FINAL POLISH - MAX button fix, QR enriquecido, validacao 2 etapas
- **29/03/2026**: CRITICAL FIX - removeChild DOM crash fix, html5-qrcode scanner
- **29/03/2026**: ADMIN UPGRADE P1 - Fundo branco, dados reais, busca de voucher com auditoria
- **29/03/2026**: ADMIN UPGRADE P2 - Aba Financeiro (receita bruta/liquida, saldo a liquidar, comissao global)

## Core Requirements (Implementados)
- [x] Modo Simulacao para ofertas
- [x] Codigo da Oferta (OFF-XXXXXX)
- [x] Links de referencia dinamicos
- [x] Dashboard financeiro do estabelecimento
- [x] Fluxo completo de creditos (deducao, transferencia, devolucao)
- [x] Vouchers persistidos com credits_used, final_price_to_pay, original_price
- [x] Validacao 2 etapas (preview + confirmar recebimento)
- [x] QR Modal estavel (displayMode state sem removeChild crash)
- [x] html5-qrcode scanner para web
- [x] Cancelamento com devolucao de creditos
- [x] Admin Dashboard: Fundo branco (#FFFFFF)
- [x] Admin Dashboard: Cards de resumo com dados reais MongoDB
- [x] Admin Dashboard: Top 5 Estabelecimentos por vendas
- [x] Admin Dashboard: Busca por codigo de voucher com modal de auditoria
- [x] Admin Financeiro: Receita Bruta (token_purchases + token_packages)
- [x] Admin Financeiro: Receita Liquida (Lucro iToke = bruta - comissoes)
- [x] Admin Financeiro: Saldo a Liquidar (withdrawable_balance dos estabelecimentos)
- [x] Admin Financeiro: Configuracao de Comissao Global (%) salva no MongoDB
- [x] Admin Financeiro: Regras de comissao informativas

## Backlog
### P1
- [ ] Edicao de ofertas existentes
- [ ] Busca Digital no Media Hub

### P2
- [ ] Restaurar Google OAuth
- [ ] Filtro de ofertas por cidade/bairro
- [ ] Refatorar server.py em APIRouters (>2500 linhas)
- [ ] Historico completo de transacoes do cliente
