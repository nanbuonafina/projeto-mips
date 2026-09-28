"""
execucao das instrucoes de multiplicacao, divisao e registradores especiais
do Tipo R (Entrega 2 - Etapa 2).

assim como em tipo_r_aritmetica_logica.py, este modulo NAO decodifica
instrucoes: ele recebe o dicionario "campos" ja montado por decoder.py e
executa a operacao correspondente.

instrucoes cobertas nesta etapa (opcode = 0x00, distinguidas por funct):
    mult, multu, div, divu, mfhi, mflo

diferenca importante em relacao ao modulo anterior: mult/multu/div/divu NAO
escrevem em rd -- elas escrevem nos registradores especiais HI e LO. quem le
HI/LO de volta para um registrador comum sao as instrucoes mfhi/mflo.

convencao adotada para HI/LO (provisoria ate criarmos registers.py, mesma
logica ja usada para "regs" no modulo anterior):
    - "especiais" e um dicionario com duas chaves, "hi" e "lo".
    - cada uma guarda um inteiro SEM SINAL de 32 bits (intervalo
      [0, 2**32 - 1]), na mesma representacao usada em "regs".
"""

from tipo_r_aritmetica_logica import (
    MASK32,
    to_signed32,
    to_unsigned32,
    ler_registrador,
    escrever_registrador,
)

# mascara de 64 bits: usada para extrair o padrao de bits de um produto de
# 64 bits (32 bits x 32 bits = ate 64 bits de resultado), do mesmo jeito que
# MASK32 (importada acima) extrai um padrao de 32 bits.
MASK64 = 0xFFFFFFFFFFFFFFFF


def _dividir_truncando_para_zero(dividendo, divisor):
    """divisao inteira com sinal que trunca em direcao a zero, como o MIPS
    (e a linguagem C) definem "div"/"rem" -- e DIFERENTE do "//" do Python,
    que arredonda para baixo (em direcao a -infinito).

    exemplo da diferenca: -7 // 2 no Python da -4 (arredonda para baixo),
    mas o MIPS espera -3 (trunca em direcao a zero, descartando a parte
    fracionaria de -3.5). por isso implementamos a divisao manualmente:
    dividimos os valores absolutos (onde "//" e "%" do Python coincidem com
    truncamento, pois ambos os operandos sao nao-negativos) e so depois
    recolocamos o sinal correto no quociente.
    """
    quociente_abs = abs(dividendo) // abs(divisor)
    sinais_diferentes = (dividendo < 0) != (divisor < 0)
    quociente = -quociente_abs if sinais_diferentes else quociente_abs
    resto = dividendo - quociente * divisor
    return quociente, resto


def executar_mult(regs, especiais, campos):
    """mult $rs, $rt -- multiplicacao COM SINAL, resultado de 64 bits.

    le rs e rt como inteiros com sinal, multiplica normalmente (o Python
    nunca estoura, entao o produto matematico exato sempre esta correto) e
    depois recorta esse produto em dois pedacos de 32 bits:
      - "& MASK64" pega o padrao de bits em complemento de dois de 64 bits
        equivalente ao produto (necessario para produtos negativos, cujo
        valor Python e negativo mas cujo padrao de bits de 64 bits e o que
        precisamos separar).
      - ">> 32" desloca os 32 bits mais significativos para a posicao mais
        baixa, isolando a metade alta do produto -> vai para HI.
      - "& MASK32" pega os 32 bits menos significativos -> vai para LO.

    mult nunca gera excecao de overflow no MIPS: o resultado de 64 bits
    sempre cabe em HI+LO, entao o "overflow" do funct add/sub simplesmente
    nao existe aqui.
    """
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    b = to_signed32(ler_registrador(regs, campos["rt"]))
    produto_64 = (a * b) & MASK64
    especiais["hi"] = (produto_64 >> 32) & MASK32
    especiais["lo"] = produto_64 & MASK32
    return False


def executar_multu(regs, especiais, campos):
    """multu $rs, $rt -- multiplicacao SEM SINAL, resultado de 64 bits.

    le rs e rt ja como valores sem sinal (nao precisa de to_signed32, pois
    ambos ja sao tratados como grandezas nao-negativas). como os dois
    operandos sao no maximo 2**32 - 1, o produto e no maximo pouco menor
    que 2**64, cabendo exatamente em HI (32 bits altos) + LO (32 bits
    baixos), sem necessidade de mascara de sinal.
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    produto_64 = (a * b) & MASK64
    especiais["hi"] = (produto_64 >> 32) & MASK32
    especiais["lo"] = produto_64 & MASK32
    return False


def executar_div(regs, especiais, campos):
    """div $rs, $rt -- divisao COM SINAL. LO recebe o quociente, HI recebe
    o resto, seguindo truncamento em direcao a zero (ver
    _dividir_truncando_para_zero).

    divisao por zero e comportamento indefinido no MIPS real (nao gera
    excecao na maioria das implementacoes). aqui optamos por NAO alterar
    HI/LO nesse caso, para nao travar a simulacao nem inventar um valor.
    """
    a = to_signed32(ler_registrador(regs, campos["rs"]))
    b = to_signed32(ler_registrador(regs, campos["rt"]))
    if b == 0:
        return False
    quociente, resto = _dividir_truncando_para_zero(a, b)
    especiais["lo"] = to_unsigned32(quociente)
    especiais["hi"] = to_unsigned32(resto)
    return False


def executar_divu(regs, especiais, campos):
    """divu $rs, $rt -- divisao SEM SINAL. LO recebe o quociente, HI recebe
    o resto.

    como os dois operandos ja sao nao-negativos, "//" e "%" do Python
    coincidem exatamente com a divisao/resto inteiros esperados pelo MIPS
    (nao ha diferenca de truncamento a considerar, ao contrario de "div").
    """
    a = ler_registrador(regs, campos["rs"])
    b = ler_registrador(regs, campos["rt"])
    if b == 0:
        return False
    especiais["lo"] = a // b
    especiais["hi"] = a % b
    return False


def executar_mfhi(regs, especiais, campos):
    """mfhi $rd -- copia o valor de HI para um registrador comum.

    e uma leitura simples, sem nenhuma operacao de bits alem da propria
    escrita em rd (que ja aplica MASK32 e a trava de $0 dentro de
    escrever_registrador).
    """
    escrever_registrador(regs, campos["rd"], especiais["hi"])
    return False


def executar_mflo(regs, especiais, campos):
    """mflo $rd -- copia o valor de LO para um registrador comum."""
    escrever_registrador(regs, campos["rd"], especiais["lo"])
    return False


# tabela funct -> funcao de execucao, mesma chave usada em decoder.py e no
# padrao ja adotado em tipo_r_aritmetica_logica.py.
TIPO_R_MULT_DIV_ESPECIAIS = {
    0x18: executar_mult,
    0x19: executar_multu,
    0x1a: executar_div,
    0x1b: executar_divu,
    0x10: executar_mfhi,
    0x12: executar_mflo,
}


def executar_tipo_r_mult_div_especiais(regs, especiais, campos):
    """ponto de entrada do modulo, no mesmo formato do modulo anterior.

    retorna (executada, overflow):
        - executada: True se o funct em "campos" pertence a este modulo.
        - overflow: sempre False aqui -- nenhuma das instrucoes deste
          modulo gera a excecao de overflow usada no campo "stdout" (ver
          docs/formato-json.md); esse campo so existe para manter a mesma
          assinatura de retorno usada por executar_tipo_r_aritmetica_logica,
          facilitando o despacho encadeado no modulo principal.
    """
    funcao = TIPO_R_MULT_DIV_ESPECIAIS.get(campos["funct"])
    if funcao is None:
        return False, False
    overflow = funcao(regs, especiais, campos)
    return True, overflow
