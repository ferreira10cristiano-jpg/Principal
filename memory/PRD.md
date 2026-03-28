# PRD - Plataforma de Ofertas de Estabelecimentos (iToke)

## Problem Statement
Refatoração do perfil "Estabelecimento" com separação de dados fixos (perfil) e variáveis (oferta), limpeza de campos duplicados, Hub de Mídia funcional e automação de links do Instagram.

## Arquitetura

### Backend (FastAPI + MongoDB)
- **Collections**: `establishments`, `offers`, `users`, `sessions`, `qr_codes`
- **Endpoints**:
  - `POST/GET/PUT /api/establishments/{id}` - Gerenciamento do estabelecimento
  - `POST/GET /api/offers` - Gerenciamento de ofertas
  - `GET /api/offers/code/{offer_code}` - Busca por código da oferta
  - `GET /api/offers/search?code=XXX` - Busca parcial por código
  - `POST /api/generate-image` - Geração de imagem via Gemini
  - `POST /api/qr-codes` - Geração de QR Code com código da oferta
  - `POST /api/auth/email-login` - Login via email (modo teste)

### Frontend (Expo React Native Web)
- `/` - Tela de Seleção (Cliente/Estabelecimento)
- `/login` - Login com Google ou Email
- `/(tabs)` - Área do Cliente (Ofertas, QR, Carteira, Ajuda, Perfil)
- `/establishment/dashboard` - Dashboard do Estabelecimento
- `/establishment/offers` - Wizard 4 passos + listagem com código e badge simulação

## User Personas
1. **Cliente** - Busca ofertas, gera QR Codes, economiza
2. **Dono de Estabelecimento** - Cria perfil uma vez, publica múltiplas ofertas
3. **Admin** - Gerencia plataforma
4. **Representante** - Gerencia parceiros

## Core Requirements (Implementados)
- [x] Separação de dados: Cidade, Bairro, Sobre, Instagram movidos para Perfil
- [x] Formulário de oferta limpo: apenas Título, Preços, Descrição única, Foto
- [x] Oferta puxa automaticamente dados do perfil
- [x] Hub de Mídia com 4 opções: Câmera, Galeria, URL, IA (Gemini)
- [x] CNPJ com validação algorítmica
- [x] Wizard 4 passos: Info → Regras → Localização → Preview
- [x] **MODO SIMULAÇÃO**: Criação de ofertas sem verificação de tokens
- [x] **CÓDIGO DA OFERTA**: Formato OFF-XXXXXX para rastreamento fácil
- [x] **BUSCA POR CÓDIGO**: Endpoints para localizar ofertas rapidamente
- [x] **BADGE SIMULAÇÃO**: Indicador visual de ofertas de teste

## Implementation Log
- **25/03/2026**: Implementação completa da refatoração inicial
- **26/03/2026**: Restauração do código do GitHub + Mock Auth
- **28/03/2026**: Correção de Navegação e Logout Global
- **28/03/2026**: Bug Fix - Botão "Publicar Oferta" não funcionava
  - Desabilitado verificação de tokens para modo simulação
- **28/03/2026**: Código Identificador de Ofertas
  - Novo campo `offer_code` formato OFF-XXXXXX
  - Novo campo `is_simulation` para identificar ofertas de teste
  - Endpoint `GET /api/offers/code/{code}` - busca exata
  - Endpoint `GET /api/offers/search?code=XXX` - busca parcial
  - QR Code inclui `offer_code` para fallback manual
  - Badge "SIMULAÇÃO" na listagem de ofertas
  - Chip com código da oferta visível no card

## Tech Stack
- Backend: FastAPI, Motor (async MongoDB), Pydantic
- Frontend: Expo (React Native Web), Expo Router, Zustand
- AI: Gemini 3.1 Flash Image Preview (via Emergent LLM Key)

## What's Been Implemented
- [x] Sistema de autenticação (email login para testes)
- [x] CRUD de estabelecimentos
- [x] CRUD de ofertas com wizard de 4 passos
- [x] Hub de mídia (câmera, galeria, IA, URL)
- [x] Sistema de QR Code com código da oferta
- [x] Dashboard do estabelecimento com métricas
- [x] Feed de ofertas para clientes
- [x] **MODO SIMULAÇÃO** - Ofertas criadas sem verificação de tokens
- [x] **CÓDIGO OFF-XXXXXX** - Identificador único e legível
- [x] **BUSCA RÁPIDA** - Localizar oferta por código (exato ou parcial)

## Backlog
### P0 (Crítico)
- [x] Bug Fix: Botão "Publicar Oferta" (RESOLVIDO)
- [x] Código identificador de ofertas (RESOLVIDO)

### P1 (Alta Prioridade)
- [ ] Edição de ofertas existentes
- [ ] Implementar "Busca Digital" (pesquisa de imagens na web) no Media Hub
- [ ] Preview de imagem antes de publicar

### P2 (Média Prioridade)
- [ ] Restaurar autenticação Firebase/Google OAuth real
- [ ] Filtro de ofertas por cidade/bairro
- [ ] Categorias de ofertas
- [ ] Notificações push para novas ofertas

### P3 (Baixa Prioridade)
- [ ] Sistema de avaliações
- [ ] Histórico de ofertas resgatadas
- [ ] Relatórios avançados para estabelecimentos

## Next Tasks
1. Testar fluxo completo de criação de ofertas no frontend
2. Implementar edição de ofertas existentes
3. Adicionar funcionalidade de "Busca Digital" no Hub de Mídia
