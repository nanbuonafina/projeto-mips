# Guia de execução

## Requisitos

- Python 3.8+ (sem dependências externas — apenas biblioteca padrão).

## Rodar o simulador

```bash
cd src
python main.py <entrada.json> <saida.json>
```

Exemplo com o caso oficial da especificação:

```bash
cd src
python main.py ../tests/test_entrega1_input.json ../output/output_entrega1.json
```

Sem argumentos, o script usa os arquivos de teste padrão:

```bash
cd src
python main.py
# equivalente a:
# python main.py ../tests/test_entrega1_input.json ../output/output_entrega1.json
```

## Arquivos de teste disponíveis

| Arquivo | Conteúdo |
|---|---|
| `tests/test_entrega1_input.json` | Exemplo oficial da especificação (`0x02114020` → `add $8, $16, $17`) |
| `tests/test_entrega1_multi.json` | Bateria com `addiu`, `lui`, `ori`, `add` e `j`, cobrindo os três formatos |

## Verificar a saída manualmente

```bash
cd src
python main.py ../tests/test_entrega1_multi.json ../output/output_multi.json
cat ../output/output_multi.json
```

O resultado esperado para `test_entrega1_input.json` é:

```json
[
  {
    "hex": "0x02114020",
    "text": "add $8, $16, $17",
    "regs": {},
    "mem": {},
    "stdout": ""
  }
]
```
