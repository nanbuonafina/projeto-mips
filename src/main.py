"""
entrega 1 - Identificador de Instrucoes MIPS.

kle um arquivo de entrada .json (campos config, data, text), decodifica cada
instrucao de 32 bits presente em "text" e gera um arquivo de saida .json com
os campos hex, text, regs, mem e stdout para cada instrucao, na mesma ordem
da entrada.
"""

import sys
from pathlib import Path

from decoder import decode_hex
from io_utils import load_input, save_output


def process(input_path, output_path):
    data = load_input(input_path)

    entries = []
    for hex_str in data["text"]:
        hex_normalized, asm_text = decode_hex(hex_str)
        entries.append({
            "hex": hex_normalized,
            "text": asm_text,
            "regs": {},
            "mem": {},
            "stdout": "",
        })

    save_output(output_path, entries)
    return entries


def main():
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        base = Path(__file__).resolve().parent.parent
        input_path = base / "tests" / "test_entrega1_input.json"
        output_path = base / "output" / "output_entrega1.json"

    entries = process(input_path, output_path)
    print(f"Entrada:  {input_path}")
    print(f"Saida:    {output_path}")
    print(f"{len(entries)} instrucao(oes) decodificada(s).")


if __name__ == "__main__":
    main()
