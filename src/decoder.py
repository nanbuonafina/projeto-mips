"""
decodificador de instrucoes MIPS (Entrega 1).

extrai os campos de uma instrucao de 32 bits (formatos R, I e J) e monta a
representacao textual (assembly) correspondente, com base nas tabelas de
docs/markdown/mips-green-sheet.md e docs/markdown/instrucoes-mips-decodificacao.md.
"""

# tabela de instrucoes tipo R: funct -> (mnemonico, layout)
# layout descreve quais campos aparecem e em que ordem no texto assembly.
R_TYPE = {
    0x20: ("add", "rd_rs_rt"),
    0x21: ("addu", "rd_rs_rt"),
    0x24: ("and", "rd_rs_rt"),
    0x1a: ("div", "rs_rt"),
    0x1b: ("divu", "rs_rt"),
    0x08: ("jr", "rs"),
    0x10: ("mfhi", "rd"),
    0x12: ("mflo", "rd"),
    0x18: ("mult", "rs_rt"),
    0x19: ("multu", "rs_rt"),
    0x27: ("nor", "rd_rs_rt"),
    0x25: ("or", "rd_rs_rt"),
    0x00: ("sll", "rd_rt_shamt"),
    0x04: ("sllv", "rd_rt_rs"),
    0x2a: ("slt", "rd_rs_rt"),
    0x2b: ("sltu", "rd_rs_rt"),
    0x03: ("sra", "rd_rt_shamt"),
    0x07: ("srav", "rd_rt_rs"),
    0x02: ("srl", "rd_rt_shamt"),
    0x06: ("srlv", "rd_rt_rs"),
    0x22: ("sub", "rd_rs_rt"),
    0x23: ("subu", "rd_rs_rt"),
    0x26: ("xor", "rd_rs_rt"),
    0x0c: ("syscall", "none"),
}

# tabela de instrucoes tipo I: opcode -> (mnemonico, layout, extensao_do_imediato)
I_TYPE = {
    0x08: ("addi", "rt_rs_imm", "signed"),
    0x09: ("addiu", "rt_rs_imm", "signed"),
    0x0c: ("andi", "rt_rs_imm", "unsigned"),
    0x04: ("beq", "rs_rt_imm", "signed"),
    0x05: ("bne", "rs_rt_imm", "signed"),
    0x07: ("bgtz", "rs_imm", "signed"),
    0x06: ("blez", "rs_imm", "signed"),
    0x01: ("bltz", "rs_imm", "signed"),
    0x20: ("lb", "rt_imm_rs", "signed"),
    0x24: ("lbu", "rt_imm_rs", "signed"),
    0x25: ("lhu", "rt_imm_rs", "signed"),
    0x0f: ("lui", "rt_imm", "unsigned"),
    0x23: ("lw", "rt_imm_rs", "signed"),
    0x0d: ("ori", "rt_rs_imm", "unsigned"),
    0x28: ("sb", "rt_imm_rs", "signed"),
    0x29: ("sh", "rt_imm_rs", "signed"),
    0x0a: ("slti", "rt_rs_imm", "signed"),
    0x0b: ("sltiu", "rt_rs_imm", "signed"),
    0x2b: ("sw", "rt_imm_rs", "signed"),
    0x0e: ("xori", "rt_rs_imm", "unsigned"),
}

# tabela de instrucoes tipo J: opcode -> mnemonico
J_TYPE = {
    0x02: "j",
    0x03: "jal",
}


def _sign_extend(value, bits):
    limit = 1 << bits
    if value >= (limit >> 1):
        value -= limit
    return value


def _split_fields(word):
    return {
        "opcode": (word >> 26) & 0x3F,
        "rs": (word >> 21) & 0x1F,
        "rt": (word >> 16) & 0x1F,
        "rd": (word >> 11) & 0x1F,
        "shamt": (word >> 6) & 0x1F,
        "funct": word & 0x3F,
        "imm": word & 0xFFFF,
        "address": word & 0x3FFFFFF,
    }


def decode_word(word):
    """decodifica um inteiro de 32 bits e retorna (mnemonico, texto_assembly, campos)."""
    fields = _split_fields(word)
    opcode = fields["opcode"]

    if opcode == 0x00:
        entry = R_TYPE.get(fields["funct"])
        if entry is None:
            return None, f".word 0x{word & 0xFFFFFFFF:08x}", fields
        mnemonic, layout = entry
        text = _format_r(mnemonic, layout, fields)
        return mnemonic, text, fields

    if opcode in J_TYPE:
        mnemonic = J_TYPE[opcode]
        text = f"{mnemonic} {fields['address']}"
        return mnemonic, text, fields

    entry = I_TYPE.get(opcode)
    if entry is not None:
        mnemonic, layout, imm_mode = entry
        text = _format_i(mnemonic, layout, imm_mode, fields)
        return mnemonic, text, fields

    return None, f".word 0x{word & 0xFFFFFFFF:08x}", fields


def _format_r(mnemonic, layout, f):
    rd, rs, rt, shamt = f["rd"], f["rs"], f["rt"], f["shamt"]
    if layout == "rd_rs_rt":
        return f"{mnemonic} ${rd}, ${rs}, ${rt}"
    if layout == "rd_rt_shamt":
        return f"{mnemonic} ${rd}, ${rt}, {shamt}"
    if layout == "rd_rt_rs":
        return f"{mnemonic} ${rd}, ${rt}, ${rs}"
    if layout == "rs_rt":
        return f"{mnemonic} ${rs}, ${rt}"
    if layout == "rs":
        return f"{mnemonic} ${rs}"
    if layout == "rd":
        return f"{mnemonic} ${rd}"
    return mnemonic


def _format_i(mnemonic, layout, imm_mode, f):
    rs, rt = f["rs"], f["rt"]
    imm = f["imm"] if imm_mode == "unsigned" else _sign_extend(f["imm"], 16)
    if layout == "rt_rs_imm":
        return f"{mnemonic} ${rt}, ${rs}, {imm}"
    if layout == "rs_rt_imm":
        return f"{mnemonic} ${rs}, ${rt}, {imm}"
    if layout == "rs_imm":
        return f"{mnemonic} ${rs}, {imm}"
    if layout == "rt_imm_rs":
        return f"{mnemonic} ${rt}, {imm}(${rs})"
    if layout == "rt_imm":
        return f"{mnemonic} ${rt}, {imm}"
    return mnemonic


def decode_hex(hex_str):
    """decodifica uma string hexadecimal de 32 bits."""
    word = int(hex_str, 16)
    mnemonic, text, fields = decode_word(word)
    normalized_hex = f"0x{word & 0xFFFFFFFF:08x}"
    return normalized_hex, text
