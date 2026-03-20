# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto segue a [Versionação Semântica](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [2.1.0] - 2026-03-20

### Added
- ✨ **Sessão Persistente**: Implementar funcionalidade "Manter logado" que persiste o login entre sessões
  - Novo módulo `database/sessao.py` para gerenciar sessão em arquivo JSON
  - Checkbox "Manter logado" na tela de login
  - Auto-login automático ao iniciar app se sessão ativa existe
  - Botão "Logout" na sidebar para limpar sessão

### Fixed
- 🔧 **Migração de Banco**: Adicionar migração automática para coluna `chave` na tabela `alimentos`
  - Resolve erro `psycopg2.errors.UndefinedColumn` em ambiente PostgreSQL
  - Função `migrar_alimentos()` verifica e adiciona coluna se necessária
  - Compatível com SQLite e PostgreSQL

- 🔧 **UX Login**: Substituir `st.success()` por `st.toast()` para mensagem de sucesso não ficar presa

## [2.0.0] - 2026-03-20

### Added
- 🎯 **Restricões Alimentares por Morador**: Sistema completo de restrições customizadas
  - Painel de administração com interface dinâmica
  - Salvamento em banco de dados
  - Regeneração automática do cardápio ao alterar restrições

- 📊 **Meta Diária e Gerenciamento de Moradores**: 
  - Definição de meta diária por morador (em gramas)
  - Suporte a múltiplos moradores com configs independentes
  - UI dinâmica no painel de alimentos

- 🍽️ **Preparos por Alimento**: 
  - Definição de preparos customizados para cada alimento
  - Suporte a múltiplos preparos por alimento
  - Regeneração parcial do cardápio mantendo dia selecionado

### Changed
- ♻️ **Refatoração Estrutural**: Normalização completa do banco de dados
  - Remoção de sufixos `_M1` e `_M2` nos alimentos
  - Molagem dinâmica de alimentos por morador
  - Melhor separação de responsabilidades na UI

### Fixed
- 🐛 Peso dos lanches agora incluído corretamente no cálculo da meta diária
- 🐛 Sincronização de painel com nova modelagem de dados
- 🐛 Manutenção do dia selecionado durante regeneração parcial
- 🐛 Consistência de nomes (macarrão/macarrao)
- 🐛 Onboarding automático se usuário sem moradores

---

## Estrutura de Versão

Versões seguem o padrão `MAJOR.MINOR.PATCH`:
- **MAJOR**: Mudanças incompatíveis na API ou estrutura de dados
- **MINOR**: Novas funcionalidades retrocompatíveis
- **PATCH**: Correções de bugs

## Convenção de Commits

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Alterações em documentação
- `refactor:` Alteração sem alteração de funcionalidade
- `perf:` Melhoria de performance
- `test:` Adição ou alteração de testes
- `chore:` Alterações de ferramentas, dependências ou configuração
