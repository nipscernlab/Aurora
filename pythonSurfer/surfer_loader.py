#!/usr/bin/env python3
"""
gtkw_to_surfron.py

Converte um arquivo .gtkw (GTKWave save file) para um arquivo .surf.ron
(configuração para o Surfer waveform viewer).

Uso:
    python gtkw_to_surfron.py input.gtkw output.surf.ron

Este script extrai principalmente a lista de sinais e agrupamentos básicos.
Funcionalidades avançadas (cursors, escalas de tempo, cores) podem ser adicionadas.
"""
import re
import sys
import json


def parse_gtkw(gtkw_path):
    """
    Lê o .gtkw e extrai sinais e grupos.
    Retorna um dict com chaves: 'signals': ["sig1", ...], 'groups': {"grp1": ["sigA", ...]}
    """
    signals = []
    groups = {}
    current_group = None

    with open(gtkw_path, 'r') as f:
        for line in f:
            # Detecta início de grupo: e.g., Group "Name"
            m_grp = re.match(r'^Group\s+"([^"]+)"', line)
            if m_grp:
                current_group = m_grp.group(1)
                groups[current_group] = []
                continue

            # Detecta adição de sinal: e.g., add "signal_path"
            m_sig = re.match(r'^add\s+"([^"]+)"', line)
            if m_sig:
                sig = m_sig.group(1)
                signals.append(sig)
                if current_group:
                    groups[current_group].append(sig)
                continue

            # Detecta saída de grupo
            if line.strip() == 'end':
                current_group = None

    return {'signals': signals, 'groups': groups}


def write_surfron(config, out_path):
    """
    Serializa dicionário em RON simples.
    """
    # Conversão básica: top-level 'signals' e 'groups'
    lines = []
    lines.append('(')

    # Signals
    lines.append('  signals: [')
    for sig in config['signals']:
        lines.append(f'    "{sig}",')
    lines.append('  ],')

    # Groups
    lines.append('  groups: {')
    for grp, sigs in config['groups'].items():
        lines.append(f'    "{grp}" => [')
        for sig in sigs:
            lines.append(f'      "{sig}",')
        lines.append('    ],')
    lines.append('  },')

    lines.append(')')

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines))


def main():
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} input.gtkw output.surf.ron")
        sys.exit(1)
    inp, outp = sys.argv[1], sys.argv[2]

    cfg = parse_gtkw(inp)
    write_surfron(cfg, outp)
    print(f"Arquivo convertido: {outp}")


if __name__ == '__main__':
    main()
