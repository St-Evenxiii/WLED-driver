"""Minimal reader for KiCad S-expression netlists (no KiCad needed)."""


def parse_sexpr(text):
    tokens, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in '()':
            tokens.append(c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while text[j] != '"':
                if text[j] == '\\':
                    j += 1
                buf.append(text[j])
                j += 1
            tokens.append(('str', ''.join(buf)))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()':
                j += 1
            tokens.append(('str', text[i:j]))
            i = j

    def build(pos):
        out = []
        while pos < len(tokens):
            t = tokens[pos]
            if t == '(':
                sub, pos = build(pos + 1)
                out.append(sub)
            elif t == ')':
                return out, pos + 1
            else:
                out.append(t[1])
                pos += 1
        return out, pos

    return build(0)[0][0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def read_netlist(path):
    root = parse_sexpr(open(path, encoding='utf-8').read())
    comps = {}
    for comp in find(find(root, 'components')[0], 'comp'):
        ref = find(comp, 'ref')[0][1]
        comps[ref] = {'value': find(comp, 'value')[0][1],
                      'footprint': find(comp, 'footprint')[0][1]}
    nets = {}
    for net in find(find(root, 'nets')[0], 'net'):
        name = find(net, 'name')[0][1]
        nets[name] = [(find(nd, 'ref')[0][1], find(nd, 'pin')[0][1])
                      for nd in find(net, 'node')]
    return comps, nets
