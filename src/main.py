"""
entrega 2 - execucao de instrucoes aritmeticas/logicas e banco de
registradores.

le um arquivo de entrada .json (campos config, data, text), decodifica cada
instrucao (reaproveitando decoder.decode_word, da Entrega 1) e agora tambem
EXECUTA cada instrucao suportada sobre um banco de registradores, gerando um
arquivo de saida .json com os campos hex, text, regs, mem e stdout para cada
instrucao, na mesma ordem da entrada (mem continua vazio: load/store e
Entrega 3).

este arquivo e o "orquestrador": ele nao implementa nenhuma operacao
aritmetica/logica/shift diretamente -- so instancia o estado (regs,
especiais, pc) e decide, para cada instrucao decodificada, qual dos 4
modulos de execucao deve trata-la.
"""

import sys
from pathlib import Path

from decoder import decode_word
from io_utils import (
    load_input,
    save_output,
    carregar_registradores_iniciais,
    montar_regs_saida,
)
from tipo_r_aritmetica_logica import executar_tipo_r_aritmetica_logica
from tipo_r_mult_div_especiais import executar_tipo_r_mult_div_especiais
from tipo_r_shift import executar_tipo_r_shift
from tipo_i_aritmetica_logica import executar_tipo_i_aritmetica_logica

# endereco inicial do PC, seguindo a convencao do MARS (segmento .text
# comeca em 0x00400000) -- ver texto explicativo sobre essa escolha.
PC_INICIAL = 0x00400000

# toda instrucao MIPS ocupa uma palavra de 32 bits = 4 bytes; e por isso que
# o PC avanca de 4 em 4, e nao de 1 em 1, a cada instrucao buscada.
TAMANHO_INSTRUCAO = 4


def executar_instrucao(regs, especiais, campos):
    """tenta executar "campos" (dicionario ja montado por decoder.py) em
    cada um dos 4 modulos de execucao, na ordem correta de despacho:

        1. opcode == 0x00 (Tipo R) -> tenta, nesta ordem, os 3 modulos de
           Tipo R (aritmetica/logica, mult/div/especiais, shift), pois eles
           sao distinguidos pelo campo "funct", que so faz sentido quando
           opcode == 0x00.
        2. qualquer outro opcode (Tipo I) -> tenta o modulo de
           aritmetica/logica com imediato.

    a ordem entre os 3 modulos de Tipo R nao importa para a CORRECAO (cada
    funct pertence a exatamente um deles), mas paramos no primeiro que
    reconhecer o funct, para nao fazer trabalho desnecessario.

    retorna (executada, overflow), no mesmo formato usado por todos os
    modulos de execucao:
        - executada: False se nenhum modulo reconheceu a instrucao (ainda
          nao implementada nesta entrega, ex.: jr, syscall, lw, beq) --
          nesse caso o banco de registradores simplesmente nao e alterado.
        - overflow: True quando a instrucao executada foi add/addi/sub e
          gerou overflow aritmetico.
    """
    if campos["opcode"] == 0x00:
        executada, overflow = executar_tipo_r_aritmetica_logica(regs, campos)
        if executada:
            return executada, overflow

        executada, overflow = executar_tipo_r_mult_div_especiais(
            regs, especiais, campos
        )
        if executada:
            return executada, overflow

        return executar_tipo_r_shift(regs, campos)

    return executar_tipo_i_aritmetica_logica(regs, campos)


def process(input_path, output_path):
    data = load_input(input_path)

    # instancia o banco de registradores (32 posicoes) ja aplicando os
    # valores pre-carregados em config.regs, e os registradores especiais
    # HI/LO, ambos comecando zerados (a especificacao nao prevê pre-carga
    # de HI/LO via config, apenas de $0-$31).
    regs = carregar_registradores_iniciais(data["config"])
    especiais = {"hi": 0, "lo": 0}
    pc = PC_INICIAL

    entries = []
    for hex_str in data["text"]:
        word = int(hex_str, 16)
        _, texto_assembly, campos = decode_word(word)
        hex_normalizado = f"0x{word & 0xFFFFFFFF:08x}"

        # avanca o PC ANTES de executar, representando a busca (fetch) da
        # instrucao atual -- em uma CPU real, o PC ja aponta para a proxima
        # instrucao assim que a atual e buscada da memoria, antes mesmo de
        # ela terminar de executar. como ainda nao ha desvios/saltos
        # (Entrega 3), o PC apenas cresce de 4 em 4 nesta etapa.
        pc += TAMANHO_INSTRUCAO

        executada, overflow = executar_instrucao(regs, especiais, campos)

        entries.append({
            "hex": hex_normalizado,
            "text": texto_assembly,
            "regs": montar_regs_saida(regs, especiais, pc),
            "mem": {},
            "stdout": "overflow" if overflow else "",
        })

    save_output(output_path, entries)
    return entries


def main():
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        base = Path(__file__).resolve().parent.parent
        input_path = base / "tests" / "test_entrega2_input.json"
        output_path = base / "output" / "output_entrega2.json"

    entries = process(input_path, output_path)
    print(f"Entrada:  {input_path}")
    print(f"Saida:    {output_path}")
    print(f"{len(entries)} instrucao(oes) executada(s).")


if __name__ == "__main__":
    main()
