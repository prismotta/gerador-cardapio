# Melhorias Recomendadas - Cardápio Digital

## ✅ Melhorias Implementadas

### Refatoração Recente (Commit be49aca)
- ✓ Adicionados type hints em `gerador.py` para melhor IDE support
- ✓ Extraída função `gerar_recheios_rap10()` para eliminar duplicação
- ✓ Removido parâmetro redundante `limite_rap10` de `gerar_cardapio()`
- ✓ Removida variável `rap10_count` agora desnecessária
- ✓ Melhorada validação em `extrair_id_refeicao()` para maior robustez
- ✓ Adicionadas docstrings detalhadas e informativas

---

## 🎯 Melhorias Futuras (Prioridade Alta)

### 1. **Constants/Configuration Centralizados** 
**Arquivo:** `config.py`
```python
# Adicionar chaves de alimentos como constantes
ALIMENTO_FRANGO_M1 = "Frango_M1"
ALIMENTO_FRANGO_M2 = "Frango_M2"
# ... etc
```
**Benefício:** Evita strings hardcoded, facilita refatorações futuras

### 2. **Type Hints em Todos os Arquivos**
**Arquivos:** `core/preparos.py`, `core/compras.py`, `core/regras.py`, `database/db.py`
```python
def calcular_lista_compras(semana: List[Dict]) -> Tuple[pd.DataFrame, float]:
    ...
```
**Benefício:** Melhor IDE autocomplete, detecção de erro mais cedo

### 3. **Extração de Função em `compras.py`**
**Problema:** Lógica de agregação repetida 3 vezes (proteína, carbo, legume)
```python
# Antes: 
totais[nome]["gramas"] += gramas
# 3x repetido

# Depois:
def _agregar_alimento(totais, nome, gramas, preco):
    ...
```
**Benefício:** DRY principle, menos bugs

### 4. **Melhor Tratamento de Erros**
**Arquivos:** `core/gerador.py`, `database/db.py`
- Criar exceções customizadas (ex: `AlimentoNaoEncontradoError`)
- Adicionar try/except blocks com mensagens úteis
- Logging estruturado

### 5. **Testes Unitários**
```python
# tests/test_gerador.py
def test_gerar_cardapio_gera_7_dias():
    ...

def test_rap10_aparece_exatamente_2_vezes():
    ...
```

### 6. **Validação de Dados**
- Adicionar Pydantic models para estruturas de dados
- Validar entrada de dados no UI antes de processar

---

## 🔧 Melhorias Futuras (Prioridade Média)

### 7. **Refatorar `preparos.py`**
Usar dicionário de lookup em lugar de múltiplos if/elif:
```python
FORMATADORES = {
    "Batata": lambda peso: f"Batata {random.choice(PREPARO_CARBO['Batata'])} ({peso}g)",
    "Mandioca": ...
}
```

### 8. **Logging**
```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Cardápio gerado para {morador}")
```

### 9. **Cachear Alimentos**
Em `app.py` e `database/db.py`, implementar cache para reduzir queries

### 10. **CLI para Testes**
```bash
python -m core.gerador --morador "Morador 1" --format json
```

---

## 📊 Código Limpo (Checklist)

- ✓ Sem sintaxe errors
- ✓ Type hints nas funções principais
- ✓ Docstrings descritivas
- ✓ DRY (Don't Repeat Yourself) - melhorado
- ⚠️ Testes - **NÃO IMPLEMENTADOS**
- ⚠️ Logging - **NÃO IMPLEMENTADO**
- ⚠️ Exceções customizadas - **NÃO IMPLEMENTADAS**

---

## 📝 Notas

- Cardápio agora garante exatamente 2x RAP10 por semana
- Frango "Na Airfryer" removido das opções
- Omelete substituído por "Ovos mexidos (2 ovos)"
- Código refatorado para melhor maintainability

---

**Última revisão:** 2026-03-20  
**Status:** ✅ Versão de Produção (com ajustes recentes)
