# Formato dos arquivos JSON

Baseado na especificação oficial (`docs/pdf/projeto-mips.pdf`, seções 8 e 9).

## Entrada

Campos: `config`, `data`, `text`. Campos não utilizados devem ser `{}`.

- **`config`**: valores pré-carregados antes da execução (não usados na Entrega 1).
  - `regs`: registradores com valor diferente de zero, nomeados com prefixo `$`
    (ex.: `"$29": 2147489648`), na ordem do MARS.
  - `mem`: endereços (string) → valor decimal de word.
- **`data`**: variáveis/valores do segmento `.data` (endereço → valor).
- **`text`**: array de strings hexadecimais, uma por instrução de 32 bits,
  processadas na mesma ordem em que aparecem.

```json
{
  "config": {},
  "data": {},
  "text": ["0x02114020"]
}
```

## Saída

Um array com um objeto por instrução de `text`, na mesma ordem, contendo:

| Campo | Descrição | Nesta etapa (Entrega 1) |
|---|---|---|
| `hex` | Instrução normalizada em hexadecimal (`0x` + 8 dígitos minúsculos) | preenchido |
| `text` | Assembly MIPS decodificado | preenchido |
| `regs` | Estado do banco de registradores após a execução | `{}` (execução ainda não existe) |
| `mem` | Estado da memória após a execução | `{}` |
| `stdout` | `"overflow"` em caso de overflow, senão vazio | `""` |

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

Regras que **já são respeitadas** pelo código e continuarão valendo nas
próximas entregas:

- Ordem de processamento = ordem do array `text` de entrada.
- Hex sempre normalizado para 8 dígitos hexadecimais em minúsculas com prefixo `0x`.
- Quando `regs`/`mem` passarem a ser preenchidos (Entregas 2/3), apenas
  registradores/endereços com valor diferente de zero devem aparecer, e a
  ordem deve ser `$0` a `$31`, depois `pc`, `hi`, `lo` (regs) / endereços
  crescentes (mem) — ver seção 9 da especificação.
