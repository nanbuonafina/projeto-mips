# Documentação — Simulador MIPS

Índice da documentação do projeto. Para a especificação original da disciplina, veja `pdf/` (material de referência, não editar).

| Documento | Conteúdo |
|---|---|
| [formato-json.md](formato-json.md) | Especificação dos arquivos de entrada e saída, com exemplos |
| [instrucoes-suportadas.md](instrucoes-suportadas.md) | Tabela completa de opcodes/functs e sintaxe assembly gerada por instrução |
| [guia-execucao.md](guia-execucao.md) | Como rodar o simulador e os testes |

## Status do projeto

- [x] **Entrega 1** — Identificação/decodificação de instruções (formatos R, I, J)
- [ ] **Entrega 2** — Execução de instruções lógicas e aritméticas, banco de registradores
- [ ] **Entrega 3** — Load, store, desvios e memória

## Estrutura de pastas

```
projeto-mips/
├── docs/
│   ├── pdf/              # especificação original em PDF
├── src/
│   ├── decoder.py         # tabelas de opcode/funct + extração de campos + formatação assembly
│   ├── io_utils.py        # leitura/escrita dos JSONs de entrada e saída
│   └── main.py            # ponto de entrada (CLI)
├── tests/                 # arquivos JSON de entrada para validação manual
└── output/                # saídas geradas pelas execuções
```

## Desenvolvedores
- Maria Fernanda Trevizane Buonafina
- Juliana Maria da Silva Venâncio
- Vitor Fernandes Dallegrave
- Vinicius Silva Rodrigues de Assis