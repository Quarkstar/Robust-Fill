import re

import ast


def evaluate(exp, value):
    if isinstance(exp, ast.Program):
        return ''.join([
            evaluate(e, value)
            for e in exp.expressions
        ])

    if isinstance(exp, ast.ApplyNesting):
        return evaluate(exp.nesting1, evaluate(exp.nesting2, value))

    if isinstance(exp, ast.ApplySubstring):
        return evaluate(exp.nesting, evaluate(exp.substring, value))

    if isinstance(exp, ast.ConstStr):
        return exp.char

    if isinstance(exp, ast.SubStr):
        p1 = exp.pos1 if exp.pos1 > 0 else len(value) + exp.pos1
        p2 = exp.pos2 if exp.pos2 > 0 else len(value) + exp.pos2
        if p1 - 1 < 0 or p2 > len(value):
            raise IndexError
        return value[p1-1:p2]

    if isinstance(exp, ast.GetSpan):
        raise NotImplementedError

    if isinstance(exp, ast.GetToken):
        matches = match_value(exp.type_, value)
        i = exp.index
        if exp.index > 0:
            # Positive indices start at 1
            i -= 1
        return matches[i]

    if isinstance(exp, ast.ToCase):
        if exp.case == ast.Case.PROPER:
            return value.capitalize()

        if exp.case == ast.Case.ALL_CAPS:
            return value.upper()

        if exp.case == ast.Case.LOWER:
            return value.lower()

        raise ValueError('Invalid case: {}'.format(exp))

    if isinstance(exp, ast.Replace):
        return value.replace(exp.delim1, exp.delim2)

    if isinstance(exp, ast.Trim):
        return value.strip()

    if isinstance(exp, ast.GetUpto):
        raise NotImplementedError

    if isinstance(exp, ast.GetFrom):
        raise NotImplementedError

    if isinstance(exp, ast.GetFirst):
        matches = match_value(exp.type_, value)

        if exp.index < 0 or exp.index > len(matches):
            raise IndexError

        return ''.join(matches[:exp.index])

    if isinstance(exp, ast.GetAll):
        return ''.join(match_value(exp.type_, value))

    raise ValueError('Unsupported operator: {}'.format(exp))


def match_value(type_, value):
    regex = regex_for_type(type_)
    return [
        t
        for t in re.findall(regex, value)
        if t != ''
    ]


def regex_for_type(type_):
    if type_ == ast.Type.NUMBER:
        return '[0-9]*'

    if type_ == ast.Type.WORD:
        return '[A-Za-z]*'

    if type_ == ast.Type.ALPHANUM:
        return '[A-Za-z0-9]*'

    if type_ == ast.Type.ALL_CAPS:
        return '[A-Z]*'

    if type_ == ast.Type.PROP_CASE:
        return '[A-Z][a-z]*'

    if type_ == ast.Type.LOWER:
        return '[a-z]*'

    if type_ == ast.Type.DIGIT:
        return '[0-9]'

    if type_ == ast.Type.CHAR:
        return '[A-Za-z]'

    raise ValueError('Unsupported type: {}'.format(type_))
