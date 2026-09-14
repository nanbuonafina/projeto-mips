"""leitura e escrita dos arquivos JSON de entrada/saida do simulador MIPS."""

import json


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
