# Instruções suportadas

Tabela derivada diretamente de `src/decoder.py` (mantenha este documento em sincronia
caso as tabelas do código sejam alteradas). Valores de opcode/funct em hexadecimal.

## Tipo R (opcode = 0x00, distinguidas por `funct`)

| Mnemônico | Funct | Sintaxe assembly gerada |
|---|---|---|
| add | 0x20 | `add $rd, $rs, $rt` |
| addu | 0x21 | `addu $rd, $rs, $rt` |
| and | 0x24 | `and $rd, $rs, $rt` |
| div | 0x1a | `div $rs, $rt` |
| divu | 0x1b | `divu $rs, $rt` |
| jr | 0x08 | `jr $rs` |
| mfhi | 0x10 | `mfhi $rd` |
| mflo | 0x12 | `mflo $rd` |
| mult | 0x18 | `mult $rs, $rt` |
| multu | 0x19 | `multu $rs, $rt` |
| nor | 0x27 | `nor $rd, $rs, $rt` |
| or | 0x25 | `or $rd, $rs, $rt` |
| sll | 0x00 | `sll $rd, $rt, shamt` |
| sllv | 0x04 | `sllv $rd, $rt, $rs` |
| slt | 0x2a | `slt $rd, $rs, $rt` |
| sltu | 0x2b | `sltu $rd, $rs, $rt` |
| sra | 0x03 | `sra $rd, $rt, shamt` |
| srav | 0x07 | `srav $rd, $rt, $rs` |
| srl | 0x02 | `srl $rd, $rt, shamt` |
| srlv | 0x06 | `srlv $rd, $rt, $rs` |
| sub | 0x22 | `sub $rd, $rs, $rt` |
| subu | 0x23 | `subu $rd, $rs, $rt` |
| xor | 0x26 | `xor $rd, $rs, $rt` |
| syscall | 0x0c | `syscall` |

## Tipo I (distinguidas por `opcode`)

| Mnemônico | Opcode | Extensão do imediato | Sintaxe assembly gerada |
|---|---|---|---|
| addi | 0x08 | signed | `addi $rt, $rs, imm` |
| addiu | 0x09 | signed | `addiu $rt, $rs, imm` |
| andi | 0x0c | unsigned | `andi $rt, $rs, imm` |
| beq | 0x04 | signed | `beq $rs, $rt, imm` |
| bne | 0x05 | signed | `bne $rs, $rt, imm` |
| bgtz | 0x07 | signed | `bgtz $rs, imm` |
| blez | 0x06 | signed | `blez $rs, imm` |
| bltz | 0x01 | signed | `bltz $rs, imm` |
| lb | 0x20 | signed | `lb $rt, imm($rs)` |
| lbu | 0x24 | signed | `lbu $rt, imm($rs)` |
| lhu | 0x25 | signed | `lhu $rt, imm($rs)` |
| lui | 0x0f | unsigned | `lui $rt, imm` |
| lw | 0x23 | signed | `lw $rt, imm($rs)` |
| ori | 0x0d | unsigned | `ori $rt, $rs, imm` |
| sb | 0x28 | signed | `sb $rt, imm($rs)` |
| sh | 0x29 | signed | `sh $rt, imm($rs)` |
| slti | 0x0a | signed | `slti $rt, $rs, imm` |
| sltiu | 0x0b | signed | `sltiu $rt, $rs, imm` |
| sw | 0x2b | signed | `sw $rt, imm($rs)` |
| xori | 0x0e | unsigned | `xori $rt, $rs, imm` |

> A extensão do imediato segue a semântica real do MIPS: instruções
> aritméticas/branch/load-store usam sign-extend (16 → 32 bits preservando o
> sinal); instruções lógicas (`andi`, `ori`, `xori`) e `lui` usam zero-extend
> (tratam o campo como valor sem sinal).

## Tipo J

| Mnemônico | Opcode | Sintaxe assembly gerada |
|---|---|---|
| j | 0x02 | `j address` |
| jal | 0x03 | `jal address` |

`address` é o campo bruto de 26 bits em decimal (sem deslocamento nem soma ao
PC), exatamente como no exemplo oficial da especificação:
`0x0810004a` → `j 1048650`.

## Registradores

Os registradores aparecem no texto assembly pelo número (`$0`–`$31`), não pelo
apelido (`$zero`, `$t0` etc.), seguindo o exemplo oficial
(`add $8, $16, $17`, não `add $t0, $s0, $s1`).

## Instruções fora da tabela

Uma palavra de 32 bits cujo opcode/funct não conste em nenhuma tabela acima é
decodificada como `.word 0x########` (ver
[decisoes-tecnicas.md](decisoes-tecnicas.md)).
