import decimal

ctx = decimal.Context()
ctx.prec = 15

def float_to_str(f):
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')