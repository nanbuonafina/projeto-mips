"""
leitura e escrita dos arquivos JSON de entrada/saida do simulador MIPS.

na Entrega 1 este modulo so tinha load_input/save_output (decodificacao
pura, sem execucao). na Entrega 2 ele ganha duas funcoes novas, responsaveis
por converter entre o formato JSON (dicionarios com chaves "$N", "pc", "hi",
"lo") e a representacao interna usada pelos modulos de execucao (lista de
32 inteiros "regs" + dicionario "especiais" com "hi"/"lo") -- essa e a
"traducao" entre o mundo do JSON e o mundo do simulador.
"""

import json

MASK32 = 0xFFFFFFFF


def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("config", {})
    data.setdefault("data", {})
    data.setdefault("text", [])
    return data


def save_output(path, entries):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")


def carregar_registradores_iniciais(config):
    """cria o banco de registradores (lista de 32 inteiros, todos zerados)
    e aplica sobre ela os valores pre-carregados em config["regs"], se
    houver (ver docs/formato-json.md, secao "config").

    as chaves de config["regs"] vem como strings no formato "$N" (ex.:
    "$29"); "lstrip('$')" remove o cifrao e "int(...)" converte o numero
    para indice da lista. cada valor e passado por "& MASK32" para garantir
    que fique dentro da faixa de 32 bits sem sinal, mesmo que o JSON de
    entrada contenha um numero fora da faixa por engano.

    $0 nunca e alterado, mesmo que o JSON de entrada tente definir "$0":
    e assim que o hardware real se comporta (escritas em $zero sao
    descartadas), entao aplicamos a mesma trava aqui na carga inicial.
    """
    regs = [0] * 32
    for chave, valor in config.get("regs", {}).items():
        indice = int(chave.lstrip("$"))
        if indice != 0:
            regs[indice] = valor & MASK32
    return regs


def montar_regs_saida(regs, especiais, pc):
    """monta o dicionario do campo "regs" de UMA entrada de saida, seguindo
    exatamente a regra de docs/formato-json.md:

        - so aparecem registradores/registradores especiais com valor
          DIFERENTE DE ZERO;
        - a ordem e $0 a $31 primeiro, depois pc, hi, lo.

    como dicionarios em Python (3.7+) preservam a ordem de insercao, basta
    inserir as chaves na ordem certa para o JSON final sair ordenado
    corretamente -- nao e preciso nenhum passo extra de ordenacao.

    $0 nunca entra no resultado: por definicao ele vale sempre 0, entao o
    proprio teste "valor != 0" ja o exclui automaticamente (nem precisamos
    de um "if indice != 0" aqui, ja que regs[0] jamais deixa de ser 0).
    """
    saida = {}
    for indice in range(1, 32):
        valor = regs[indice]
        if valor != 0:
            saida[f"${indice}"] = valor
    if pc != 0:
        saida["pc"] = pc
    if especiais["hi"] != 0:
        saida["hi"] = especiais["hi"]
    if especiais["lo"] != 0:
        saida["lo"] = especiais["lo"]
    return saida
