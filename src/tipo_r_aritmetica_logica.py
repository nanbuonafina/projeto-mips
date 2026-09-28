"""
execucao das instrucoes aritmeticas e logicas do Tipo R (Entrega 2 - Etapa 1).

este modulo NAO decodifica instrucoes (isso ja foi feito em decoder.py, na
Entrega 1). ele recebe o dicionario de campos que decoder.py ja extraiu de
uma palavra de 32 bits (rd, rs, rt, funct, ...) e executa a operacao
correspondente sobre o banco de registradores.

instrucoes cobertas nesta etapa (opcode = 0x00, distinguidas por funct):
    add, addu, sub, subu, and, or, xor, nor, slt

convencao adotada para o banco de registradores (provisoria ate criarmos
registers.py):
    - "regs" e uma lista/sequencia mutavel com 32 posicoes (indices 0 a 31).
    - cada posicao guarda um inteiro SEM SINAL de 32 bits, ou seja, sempre
      dentro do intervalo [0, 2**32 - 1].
    - regs[0] ($zero) e sempre lido como 0, e escritas em rd == 0 sao
      ignoradas (o hardware do MIPS trava esse registrador em zero).
"""

# mascara de 32 bits: qualquer valor & MASK32 fica limitado a 32 bits,
# descartando estouros que o Python (que tem inteiros de tamanho arbitrario)
# nao faria sozinho.
MASK32 = 0xFFFFFFFF

# bit mais significativo de uma palavra de 32 bits (bit de sinal no
# complemento de dois). usado para descobrir se um valor "sem sinal" deveria
# ser interpretado como negativo.
BIT_SINAL = 0x80000000

# maior e menor valor representavel em complemento de dois de 32 bits.
# usados apenas para detectar overflow em add/sub.
INT32_MAX = 2 ** 31 - 1
INT32_MIN = -(2 ** 31)


def to_signed32(valor):
    """reinterpreta um inteiro sem sinal de 32 bits como inteiro com sinal.

    ex.: 0xFFFFFFFF (sem sinal) deve virar -1 (com sinal), pois em
    complemento de dois todos os bits em 1 representam -1.
    """
    valor &= MASK32
    if valor & BIT_SINAL:
        # bit de sinal ligado -> valor negativo. subtrai 2**32 para obter
        # o equivalente em complemento de dois (ex.: 0xFFFFFFFF -> -1).
        valor -= (1 << 32)
    return valor


def to_unsigned32(valor):
    """normaliza qualquer inteiro (positivo, negativo ou maior que 32 bits)
    para a representacao sem sinal de 32 bits usada nos registradores.

    o operador "&" com MASK32 (0xFFFFFFFF) mantem apenas os 32 bits menos
    significativos. para numeros negativos, o Python usa complemento de
    dois "infinito" internamente, entao a mascara ja produz o padrao de
    bits correto (ex.: -1 & 0xFFFFFFFF == 0xFFFFFFFF).
    """
    return valor & MASK32


def ler_registrador(regs, indice):
    """le um registrador como valor sem sinal de 32 bits.

    forca $0 a sempre valer 0, mesmo que por algum bug a posicao 0 da lista
    tenha sido alterada — e uma trava de seguranca redundante com a de
    escrever_registrador, mas barata e evita bugs silenciosos.
    """
    if indice == 0:
        return 0
    return regs[indice] & MASK32


def escrever_registrador(regs, indice, valor):
    """escreve um valor (ja normalizado para 32 bits sem sinal) em rd.

    $0 nunca e escrito: qualquer instrucao que tenha rd == 0 simplesmente
    nao tem efeito sobre o banco de registradores.
    """
    if indice == 0:
        return
    regs[indice] = valor & MASK32


def _soma_com_overflow(a_signed, b_signed):
    """calcula a soma de dois inteiros com sinal e informa se o resultado
    NAO cabe em 32 bits com sinal (overflow aritmetico).

    como o Python trabalha com inteiros de precisao arbitraria, a soma
    "a_signed + b_signed" nunca estoura sozinha: ela da sempre o resultado
    matematico exato. o overflow do MIPS e definido como "o resultado real
    nao cabe no intervalo [-2**31, 2**31 - 1]", entao basta comparar a soma
    exata contra esse intervalo para saber se o hardware real teria gerado
    uma excecao de overflow.

    (a regra classica ensinada em arquitetura — "overflow ocorre quando os
    dois operandos tem o mesmo sinal e o resultado tem sinal diferente" — e
    equivalente a esse teste de intervalo; usamos o teste de intervalo aqui
    por ser direto de implementar e igualmente correto.)
    """
    resultado = a_signed + b_signed
    overflow = resultado < INT32_MIN or resultado > INT32_MAX
    return resultado, overflow


def executar_add(regs, campos):
    """add $rd, $rs, $rt -- soma com sinal, com deteccao de overflow."""
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    b = to_signed32(ler_registrador(regs, campos["rt"]))
    resultado, overflow = _soma_com_overflow(a, b)
    if overflow:
        # segue a semantica do MIPS real: em overflow o registrador de
        # destino NAO e alterado (a excecao interrompe a instrucao antes
        # do write-back).
        return True
    escrever_registrador(regs, campos["rd"], to_unsigned32(resultado))
    return False


def executar_addu(regs, campos):
    """addu $rd, $rs, $rt -- soma sem deteccao de overflow (wrap silencioso).

    le e escreve diretamente em valores sem sinal: se a soma passar de
    2**32 - 1, a mascara MASK32 (aplicada dentro de escrever_registrador)
    descarta o bit de "vai um" extra, produzindo o mesmo resultado que um
    somador de 32 bits em hardware, sem levantar excecao.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], a + b)
    return False


def executar_sub(regs, campos):
    """sub $rd, $rs, $rt -- subtracao com sinal, com deteccao de overflow."""
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    b = to_signed32(ler_registrador(regs, campos["rt"]))
    resultado, overflow = _soma_com_overflow(a, -b)
    if overflow:
        return True
    escrever_registrador(regs, campos["rd"], to_unsigned32(resultado))
    return False


def executar_subu(regs, campos):
    """subu $rd, $rs, $rt -- subtracao sem deteccao de overflow.

    a mascara MASK32 (dentro de escrever_registrador) cuida do caso
    rt > rs: o resultado matematico seria negativo, e a mascara o converte
    para o padrao de bits sem sinal equivalente (ex.: 3 - 5 = -2 vira
    0xFFFFFFFE), exatamente como um subtrator de 32 bits em hardware.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], a - b)
    return False


def executar_and(regs, campos):
    """and $rd, $rs, $rt -- AND bit a bit.

    cada bit do resultado e 1 somente se o bit correspondente for 1 em
    AMBOS os operandos. como os dois valores ja estao mascarados em 32
    bits, o "&" do Python opera exatamente como uma porta AND por bit.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], a & b)
    return False


def executar_or(regs, campos):
    """or $rd, $rs, $rt -- OR bit a bit.

    cada bit do resultado e 1 se o bit correspondente for 1 em pelo menos
    um dos operandos.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], a | b)
    return False


def executar_xor(regs, campos):
    """xor $rd, $rs, $rt -- OU-exclusivo bit a bit.

    cada bit do resultado e 1 se os bits correspondentes dos operandos
    forem DIFERENTES entre si (1^0 ou 0^1), e 0 se forem iguais.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], a ^ b)
    return False


def executar_nor(regs, campos):
    """nor $rd, $rs, $rt -- NOR bit a bit (negacao do OR).

    o Python nao tem um operador NOR direto, entao calculamos OR e depois
    invertemos cada bit com XOR contra MASK32 (0xFFFFFFFF, ou seja, 32 bits
    todos em 1). fazer "valor ^ MASK32" inverte cada bit de "valor": onde
    MASK32 tem 1, o XOR troca o bit; como MASK32 e todo 1, TODOS os bits
    sao trocados -- e exatamente a definicao de complemento bit a bit (NOT)
    restrito a 32 bits.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    escrever_registrador(regs, campos["rd"], (a | b) ^ MASK32)
    return False


def executar_slt(regs, campos):
    """slt $rd, $rs, $rt -- "set on less than", comparacao com sinal.

    rd recebe 1 se rs < rt (interpretados como inteiros com sinal), ou 0
    caso contrario. e por isso que convertemos com to_signed32 antes de
    comparar: comparar os valores sem sinal daria resultado errado sempre
    que um deles tiver o bit mais significativo ligado (ex.: sem sinal,
    0xFFFFFFFF isto e, 4294967295, pareceria "maior" que 1; com sinal,
    0xFFFFFFFF e -1, que e menor que 1 -- e essa a resposta correta do
    slt real).
    """
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    b = to_signed32(ler_registrador(regs, campos["rt"]))
    escrever_registrador(regs, campos["rd"], 1 if a < b else 0)
    return False


# tabela funct -> funcao de execucao. mesma chave (funct) usada na tabela
# R_TYPE de decoder.py, para que o modulo principal consiga despachar a
# instrucao ja decodificada sem duplicar a logica de identificacao.
TIPO_R_ARITMETICA_LOGICA = {
    0x20: executar_add,
    0x21: executar_addu,
    0x22: executar_sub,
    0x23: executar_subu,
    0x24: executar_and,
    0x25: executar_or,
    0x26: executar_xor,
    0x27: executar_nor,
    0x2a: executar_slt,
}


def executar_tipo_r_aritmetica_logica(regs, campos):
    """ponto de entrada do modulo: executa a instrucao Tipo R descrita em
    "campos" (formato de decoder.py) se ela pertencer a este modulo.

    retorna uma tupla (executada, overflow):
        - executada: True se o funct em "campos" era uma das instrucoes
          deste modulo (e portanto a instrucao ja foi executada). False se
          o funct nao pertence a este modulo (cabe ao modulo principal
          tentar outro modulo, ex.: shift/mult/div).
        - overflow: True somente quando "executada" e True e a instrucao
          era add/sub e gerou overflow de acordo com _soma_com_overflow.
          o modulo principal deve usar isso para preencher o campo
          "stdout" da saida com "overflow" (ver docs/formato-json.md).
    """
    funcao = TIPO_R_ARITMETICA_LOGICA.get(campos["funct"])
    if funcao is None:
        return False, False
    overflow = funcao(regs, campos)
    return True, overflow
