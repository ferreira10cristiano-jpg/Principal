# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Plataforma de fidelidade e ofertas para estabelecimentos e clientes. Estabelecimentos criam ofertas com descontos, clientes geram QR Codes (vouchers) para resgatar ofertas, e o sistema rastreia vendas, creditos e comissoes de indicacao.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`, `vouchers`, `sales_history`, `financial_logs`, `client_tokens`, `client_credits`, `referral_network`, `transactions`, `token_purchases`, `platform_settings`, `withdrawal_requests`

### Frontend (Expo React Native Web)
- Admin Dashboard: 4 abas (Geral, Financeiro, Saques, Usuarios)
- Wallet: Banner → Indique e Ganhe (código + botões) → Ativos → Ganhos → Minha Rede → Histórico

## Implementation Log
- **25-28/03/2026**: MVP completo
- **28/03/2026**: CRITICAL REFACTOR - Vouchers, backup codes, scanner
- **29/03/2026**: CRITICAL FIX - removeChild DOM crash, html5-qrcode
- **29/03/2026**: ADMIN P1-P3 - Dashboard completo com 4 abas
- **29/03/2026**: FINAL POLISH - 6 melhorias UX
- **30/03/2026**: UI AJUSTE - Botões indicação reposicionados no topo da Carteira, mensagem referral atualizada

## Core Requirements (Implementados)
- [x] Fluxo completo de ofertas, QR, vouchers, creditos
- [x] Validacao 2 etapas (preview + confirmar recebimento)
- [x] html5-qrcode scanner para web
- [x] Admin: Dashboard completo com 4 abas
- [x] Admin: Busca voucher, receita, comissao global, saques, usuarios
- [x] 14 categorias de ofertas
- [x] Dias da semana com nomes completos
- [x] QR Code persiste na tela, X → Meus QR
- [x] MAX button abaixo do campo de creditos
- [x] Botões Indicar Amigo/Loja reposicionados no topo da Carteira (abaixo do banner verde)
- [x] Mensagem referral: "Olá! Olha que aplicativo fantástico..."

## Backlog
### P1
- [ ] Edicao de ofertas existentes
- [ ] Busca Digital no Media Hub

### P2
- [ ] Restaurar Google OAuth
- [ ] Filtro de ofertas por cidade/bairro
- [ ] Refatorar server.py em APIRouters (>2700 linhas)
- [ ] Historico completo de transacoes do cliente
