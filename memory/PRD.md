# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Plataforma de fidelidade e ofertas para estabelecimentos e clientes. Estabelecimentos criam ofertas com descontos, clientes geram QR Codes (vouchers) para resgatar ofertas, e o sistema rastreia vendas, creditos e comissoes de indicacao.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`, `vouchers`, `sales_history`, `financial_logs`, `client_tokens`, `client_credits`, `referral_network`, `transactions`
- **Endpoints Principais**:
  - `POST /api/auth/email-login` - Login via email
  - `POST /api/qr/generate` - Gera voucher QR (deduz 1 token + creditos IMEDIATO)
  - `POST /api/qr/validate` - Step 1: Preview do voucher (sem finalizar)
  - `POST /api/qr/confirm` - Step 2: Confirma recebimento, finaliza venda
  - `GET /api/vouchers/my` - Vouchers do cliente
  - `POST /api/vouchers/{id}/cancel` - Cancela e devolve creditos
  - `GET /api/establishments/me/sales-history` - Historico de vendas

### Frontend (Expo React Native Web)
- **QRModal**: displayMode state (generate/loading/result) com transicao segura via setTimeout
- **QR Fullscreen**: Valor Original (riscado), Creditos Aplicados (vermelho), Valor Final (verde)
- **Meus QR**: Cards com breakdown de preco, backup code, botao cancelar
- **Validate (Estabelecimento)**: html5-qrcode para scanner web + input manual + 2 etapas

## Implementation Log
- **25-28/03/2026**: MVP completo com ofertas, QR codes, validacao
- **28/03/2026**: CRITICAL REFACTOR - Vouchers persistidos, backup codes, camera scanner
- **28/03/2026**: URGENT REFACTOR - Deducao imediata de creditos, cancelamento com devolucao
- **28/03/2026**: FINAL POLISH - MAX button fix, QR enriquecido, validacao 2 etapas
- **29/03/2026**: CRITICAL FIX - removeChild DOM crash fix (displayMode state), html5-qrcode scanner

## Core Requirements (Implementados)
- [x] Modo Simulacao para ofertas
- [x] Codigo da Oferta (OFF-XXXXXX)
- [x] Links de referencia dinamicos
- [x] Dashboard financeiro do estabelecimento
- [x] Fluxo completo de creditos (deducao, transferencia, devolucao)
- [x] Vouchers persistidos com credits_used, final_price_to_pay, original_price
- [x] Validacao 2 etapas (preview + confirmar recebimento)
- [x] QR Modal estavel (displayMode state sem removeChild crash)
- [x] MAX button integrado com auto-fill e calculo real-time
- [x] QR Fullscreen enriquecido
- [x] html5-qrcode scanner para web
- [x] Cancelamento com devolucao de creditos
- [x] Financial logs com status "totalmente_pago"
- [x] Sem falsos erros em creditos parciais

## Backlog
### P1
- [ ] Edicao de ofertas existentes
- [ ] Busca Digital no Media Hub

### P2
- [ ] Restaurar Google OAuth
- [ ] Filtro de ofertas por cidade/bairro
- [ ] Refatorar server.py em APIRouters (>2300 linhas)
- [ ] Historico completo de transacoes do cliente
