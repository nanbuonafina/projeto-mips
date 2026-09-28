"""
execucao das instrucoes aritmeticas e logicas do Tipo I com imediato
(Entrega 2 - Etapa 3).

assim como nos dois modulos anteriores, este modulo NAO decodifica
instrucoes: recebe o dicionario "campos" ja montado por decoder.py e executa
a operacao correspondente. a diferenca em relacao ao Tipo R e que aqui a
instrucao e distinguida pelo "opcode" (nao pelo "funct", que so existe em
Tipo R), e um dos operandos vem do campo imediato de 16 bits ("imm"), nao de
um terceiro registrador.

instrucoes cobertas nesta etapa (distinguidas por opcode):
    addi, addiu, slti, andi, ori, xori

reaproveitamos de tipo_r_aritmetica_logica.py as mesmas funcoes/constantes
de manipulacao de registradores e de bits (MASK32, to_signed32, to_unsigned32,
INT32_MIN/MAX, ler_registrador, escrever_registrador) para nao duplicar essa
logica -- as regras de representacao dos registradores sao as mesmas em
qualquer modulo do simulador.
"""

from tipo_r_aritmetica_logica import (
    MASK32,
    INT32_MIN,
    INT32_MAX,
    to_signed32,
    to_unsigned32,
    ler_registrador,
    escrever_registrador,
)


def estender_sinal_16(imm):
    """estende um campo imediato de 16 bits para um inteiro com sinal de
    32 bits ("sign-extend").

    o campo "imm" que vem de decoder.py ja e um valor de 16 bits sem sinal
    (0 a 0xFFFF, pois foi extraido com "word & 0xFFFF"). para reinterpreta-lo
    como um numero negativo quando o bit mais significativo do campo (bit
    15, mascara 0x8000) estiver ligado, subtraimos 2**16 -- exatamente a
    mesma ideia de to_signed32, so que para um campo de 16 bits em vez de
    32. o resultado e um inteiro Python comum (positivo ou negativo) pronto
    para entrar em contas com sinal, como add/slt.

    exemplo: imm = 0xFFFF (16 bits todos em 1) representa -1 tanto em 16
    quanto em 32 bits -- e por isso "estender com sinal" apenas repete o
    bit 15 para a esquerda ate completar 32 bits, o que preserva o valor
    numerico negativo.
    """
    imm &= 0xFFFF
    if imm & 0x8000:
        imm -= 1 << 16
    return imm


def estender_zero_16(imm):
    """estende um campo imediato de 16 bits para 32 bits preenchendo com
    zeros a esquerda ("zero-extend") -- usado por andi/ori/xori.

    diferente do sign-extend, aqui NAO ha nenhuma conta a fazer: preencher
    os 16 bits superiores com zero nao muda o valor numerico do campo (ao
    contrario de repetir o bit de sinal). por isso esta funcao apenas
    aplica "& 0xFFFF" para garantir que o valor esteja limitado a 16 bits
    -- e o padrao de bits resultante, interpretado em 32 bits, ja e
    exatamente o zero-extend correto.
    """
    return imm & 0xFFFF


def executar_addi(regs, campos):
    """addi $rt, $rs, imm -- soma com sinal (imediato com sign-extend),
    COM deteccao de overflow, igual a "add" do Tipo R.

    a unica diferenca de "executar_add" (modulo anterior) e que um dos
    operandos vem de estender_sinal_16(imm) em vez de um segundo
    registrador. a logica de overflow e identica: o resultado matematico
    exato precisa caber no intervalo [-2**31, 2**31 - 1]; se nao couber, rt
    NAO e escrito (mesma semantica de excecao do "add").
    """
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    imm = estender_sinal_16(campos["imm"])
    resultado = a + imm
    overflow = resultado < INT32_MIN or resultado > INT32_MAX
    if overflow:
        return True
    escrever_registrador(regs, campos["rt"], to_unsigned32(resultado))
    return False


def executar_addiu(regs, campos):
    """addiu $rt, $rs, imm -- soma sem deteccao de overflow.

    atencao a pegadinha classica do MIPS: apesar do sufixo "u" (de
    "unsigned"), addiu AINDA usa o imediato com SIGN-EXTEND (nao
    zero-extend). o "u" so significa "nao gera excecao de overflow", nao
    "trata o imediato como sem sinal". por isso chamamos
    estender_sinal_16 aqui tambem, exatamente como em addi -- a unica
    diferenca real para addi e que nao checamos o intervalo de overflow,
    deixando a mascara MASK32 (dentro de escrever_registrador) absorver
    qualquer estouro silenciosamente.
    """
    a = ler_registrador(regs, campos["rs"])
    imm = estender_sinal_16(campos["imm"])
    escrever_registrador(regs, campos["rt"], to_unsigned32(a + imm))
    return False


def executar_slti(regs, campos):
    """slti $rt, $rs, imm -- "set on less than immediate", comparacao com
    sinal entre rs e o imediato.

    rt recebe 1 se rs < imm (ambos interpretados com sinal), ou 0 caso
    contrario -- mesma logica de executar_slt do Tipo R, trocando o
    segundo operando por estender_sinal_16(imm).
    """
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    imm = estender_sinal_16(campos["imm"])
    escrever_registrador(regs, campos["rt"], 1 if a < imm else 0)
    return False


def executar_andi(regs, campos):
    """andi $rt, $rs, imm -- AND bit a bit entre rs e o imediato.

    instrucoes logicas (andi/ori/xori) usam ZERO-extend, nao sign-extend:
    como cada bit do AND so depende do bit correspondente em cada operando,
    preencher os 16 bits superiores do imediato com 1 (como sign-extend
    faria para valores negativos) mudaria o resultado da operacao logica de
    forma que nao corresponde a intencao de "aplicar uma mascara de 16
    bits" -- por isso o MIPS usa zero-extend aqui, e nunca sign-extend.
    """
    a = ler_registrador(regs, campos["rs"])
    imm = estender_zero_16(campos["imm"])
    escrever_registrador(regs, campos["rt"], a & imm)
    return False


def executar_ori(regs, campos):
    """ori $rt, $rs, imm -- OR bit a bit entre rs e o imediato
    (zero-extend), mesma logica de executar_andi trocando o operador.
    """
    a = ler_registrador(regs, campos["rs"])
    imm = estender_zero_16(campos["imm"])
    escrever_registrador(regs, campos["rt"], a | imm)
    return False


def executar_xori(regs, campos):
    """xori $rt, $rs, imm -- XOR bit a bit entre rs e o imediato
    (zero-extend), mesma logica de executar_andi trocando o operador.
    """
    a = ler_registrador(regs, campos["rs"])
    imm = estender_zero_16(campos["imm"])
    escrever_registrador(regs, campos["rt"], a ^ imm)
    return False


# tabela opcode -> funcao de execucao. usa "opcode" (nao "funct", que so
# existe quando opcode == 0x00) porque e assim que o Tipo I e distinguido,
# igual a tabela I_TYPE de decoder.py.
TIPO_I_ARITMETICA_LOGICA = {
    0x08: executar_addi,
    0x09: executar_addiu,
    0x0a: executar_slti,
    0x0c: executar_andi,
    0x0d: executar_ori,
    0x0e: executar_xori,
}


def executar_tipo_i_aritmetica_logica(regs, campos):
    """ponto de entrada do modulo, no mesmo formato dos dois modulos
    anteriores.

    retorna (executada, overflow):
        - executada: True se o opcode em "campos" pertence a este modulo.
        - overflow: True somente quando "executada" e True e a instrucao
          era addi e gerou overflow (a unica instrucao deste modulo capaz
          de gerar overflow, assim como "add" no Tipo R). o modulo
          principal deve usar isso para preencher "stdout" com "overflow"
          (ver docs/formato-json.md).
    """
    funcao = TIPO_I_ARITMETICA_LOGICA.get(campos["opcode"])
    if funcao is None:
        return False, False
    overflow = funcao(regs, campos)
    return True, overflow
