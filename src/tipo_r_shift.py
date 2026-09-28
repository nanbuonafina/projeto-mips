"""
execucao das instrucoes de deslocamento de bits (shift) do Tipo R
(Entrega 2 - Etapa 4).

mesmo padrao dos modulos anteriores: recebe "campos" ja montado por
decoder.py e executa a operacao. reaproveitamos de tipo_r_aritmetica_logica.py
as mesmas funcoes/constantes de manipulacao de registradores e bits.

instrucoes cobertas nesta etapa (opcode = 0x00, distinguidas por funct):
    sll, srl, sra   -- deslocamento por uma quantidade FIXA (campo shamt)
    sllv, srlv, srav -- deslocamento por uma quantidade VARIAVEL (registrador rs)

em todas elas, o valor deslocado vem de rt e o resultado vai para rd -- so
muda de onde vem a QUANTIDADE de bits a deslocar (shamt fixo no primeiro
grupo, conteudo de um registrador no segundo).
"""

from tipo_r_aritmetica_logica import (
    MASK32,
    to_signed32,
    to_unsigned32,
    ler_registrador,
    escrever_registrador,
)


def executar_sll(regs, campos):
    """sll $rd, $rt, shamt -- shift logico para a ESQUERDA por "shamt" bits
    (campo fixo de 5 bits, extraido por decoder.py como campos["shamt"]).

    "<<" em Python nunca perde bits (inteiros de precisao arbitraria), entao
    aplicamos "& MASK32" depois de deslocar para descartar os bits que
    ultrapassam a posicao 31 -- exatamente o que um deslocador de hardware
    de 32 bits faria automaticamente. os bits que entram pela direita sao
    sempre 0 (e por isso "shift LOGICO": nunca olha para o sinal do valor).

    obs.: a codificacao com rd = rs = rt = shamt = 0 e o proprio "nop" do
    MIPS -- nao precisamos tratar esse caso separadamente, pois escrever em
    rd == 0 ja e ignorado por escrever_registrador.
    """
    valor = ler_registrador(regs, campos["rt"])
    quantidade = campos["shamt"]
    resultado = (valor << quantidade) & MASK32
    escrever_registrador(regs, campos["rd"], resultado)
    return False


def executar_srl(regs, campos):
    """srl $rd, $rt, shamt -- shift logico para a DIREITA por "shamt" bits.

    como ler_registrador ja devolve o valor na representacao SEM SINAL
    (0 a 2**32 - 1), o operador ">>" do Python opera exatamente como um
    shift logico: os bits que entram pela esquerda sao sempre 0, porque o
    Python nunca "inventa" bits de sinal para um inteiro que ja e
    nao-negativo. nao e preciso mascarar o resultado, pois deslocar para a
    direita so pode diminuir o valor, nunca ultrapassar 32 bits.
    """
    valor = ler_registrador(regs, campos["rt"])
    quantidade = campos["shamt"]
    resultado = valor >> quantidade
    escrever_registrador(regs, campos["rd"], resultado)
    return False


def executar_sra(regs, campos):
    """sra $rd, $rt, shamt -- shift ARITMETICO para a direita por "shamt"
    bits: preserva o bit de sinal (os bits que entram pela esquerda
    repetem o bit mais significativo original, em vez de sempre 0).

    a diferenca para srl esta so em UMA linha: aqui convertemos o valor
    para signed com to_signed32 ANTES de deslocar. o Python, para inteiros
    negativos, ja implementa ">>" como shift aritmetico nativamente (ex.:
    -8 >> 1 == -4, preservando o sinal) -- entao basta interpretar o valor
    como negativo primeiro que o proprio operador do Python faz o trabalho
    de repetir o bit de sinal. depois convertemos de volta para a
    representacao sem sinal de 32 bits com to_unsigned32, para poder
    gravar no registrador.
    """
    valor = to_signed32(ler_registrador(regs, campos["rt"]))
    quantidade = campos["shamt"]
    resultado = valor >> quantidade
    escrever_registrador(regs, campos["rd"], to_unsigned32(resultado))
    return False


def executar_sllv(regs, campos):
    """sllv $rd, $rt, $rs -- igual a sll, mas a quantidade de bits a
    deslocar vem do registrador rs, nao de um campo fixo da instrucao.

    o MIPS usa apenas os 5 bits menos significativos de rs como quantidade
    de deslocamento (mascara 0x1F = 0b11111): como um registrador so tem 32
    bits, qualquer deslocamento de 32 ou mais posicoes esvaziaria o valor
    inteiro, entao a arquitetura simplesmente ignora os bits de rs alem do
    necessario para representar 0 a 31.
    """
    valor = ler_registrador(regs, campos["rt"])
    quantidade = ler_registrador(regs, campos["rs"]) & 0x1F
    resultado = (valor << quantidade) & MASK32
    escrever_registrador(regs, campos["rd"], resultado)
    return False


def executar_srlv(regs, campos):
    """srlv $rd, $rt, $rs -- igual a srl, mas a quantidade vem dos 5 bits
    menos significativos do registrador rs (ver executar_sllv).
    """
    valor = ler_registrador(regs, campos["rt"])
    quantidade = ler_registrador(regs, campos["rs"]) & 0x1F
    resultado = valor >> quantidade
    escrever_registrador(regs, campos["rd"], resultado)
    return False


def executar_srav(regs, campos):
    """srav $rd, $rt, $rs -- igual a sra, mas a quantidade vem dos 5 bits
    menos significativos do registrador rs (ver executar_sllv).
    """
    valor = to_signed32(ler_registrador(regs, campos["rt"]))
    quantidade = ler_registrador(regs, campos["rs"]) & 0x1F
    resultado = valor >> quantidade
    escrever_registrador(regs, campos["rd"], to_unsigned32(resultado))
    return False


# tabela funct -> funcao de execucao, mesma chave usada em decoder.py e nos
# modulos anteriores. atencao: funct 0x00 tambem corresponde a "nop" (todos
# os campos zerados) -- ele cai naturalmente em executar_sll com shamt = 0,
# que e um deslocamento por zero bits, ou seja, sem nenhum efeito.
TIPO_R_SHIFT = {
    0x00: executar_sll,
    0x02: executar_srl,
    0x03: executar_sra,
    0x04: executar_sllv,
    0x06: executar_srlv,
    0x07: executar_srav,
}


def executar_tipo_r_shift(regs, campos):
    """ponto de entrada do modulo, no mesmo formato dos modulos anteriores.

    retorna (executada, overflow):
        - executada: True se o funct em "campos" pertence a este modulo.
        - overflow: sempre False -- nenhuma instrucao de shift gera a
          excecao de overflow usada no campo "stdout" (ver
          docs/formato-json.md); o campo e mantido so para preservar a
          mesma assinatura de retorno dos outros modulos de execucao,
          simplificando o despacho encadeado no modulo principal.
    """
    funcao = TIPO_R_SHIFT.get(campos["funct"])
    if funcao is None:
        return False, False
    overflow = funcao(regs, campos)
    return True, overflow
