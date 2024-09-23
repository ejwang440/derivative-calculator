from math import factorial, pi, sin, cos
from symbolic import remove_parens, is_x, is_registered_function, cleanup, is_number, has_x, to_number, has_no_ops
from parsing import get_next_split
import matplotlib.pyplot as plt


def registered_function_ddx(fun):
    if fun == 'sin':
        return 'cos'
    elif fun == 'cos':
        return '-1*sin'
    else:
        raise Exception("Unsupported function, not registered...")


def ddx(f):
    f = remove_parens(f)
    if is_x(f):
        return "1"
    elif has_no_ops(f) and is_registered_function(f):
        i = f.index('(')
        ddfun = registered_function_ddx(f[0:i])
        return ddfun + '(' + cleanup(f[i:]) + ') * ' + ddx(f[i:])
    elif is_number(f) or not has_x(f):
        return "0"
    else:
        s = get_next_split(f)
        left = f[0:s].strip()
        op = f[s]
        right = f[s+1:].strip()

        if op == "+":
            result = ddx(left) + " + " + ddx(right)
        elif op == "-":
            result = ddx(left) + " - " + ddx(right)
        elif op == "*":
            result = right + "*" + ddx(left) + " + " + left+"*"+ddx(right)
        elif op == "/":
            result = ddx(left+"*"+(right+"^"+"(-1)"))
            # result = (right+"^"+(-1))+"*"+ddx(left) + " + " + left+"*"+ddx((right+"^"+(-1)))
        elif op == "^":
            if has_x(left) and is_number(right):
                result = right*(left+"^"+(right-1))
            else:
                raise Exception(str(f) + " is not covered")
        else:
            raise Exception(str(op) + " is not covered")
    return cleanup(result)


def taylor(f, N, A):
    tay = ""
    deriv = ""
    for i in range(0, N+1):

        fact = factorial(i)

        if i == 0:
            tay += f.replace("x", A)

        else:
            deriv = f
            for a in range(1, i+1):
                deriv = ddx(deriv)
            der_string = deriv.replace("x", A)
            tay += f"+ {der_string} * (x{A})^({i})/{fact}"

    return tay


def try_function(name, f, x, A):
    approx = taylor(f, 7, "-" + A)
    print(f, "≈", approx)
    print(f.replace("x", x + " - " + A), "≈",
          eval(approx.replace("^", "**").replace("x", x)))

    plt.clf()
    R = [x * 0.1 for x in range(100)]
    plt.plot(R, [eval(approx.replace("^", "**").replace("x", str(x)))
             for x in R], color='C0')
    plt.plot(R, [eval(f.replace("^", "**").replace("x", str(x)))
             for x in R], color='C1')
    plt.savefig(name + ".png")


try_function("two-plus-x", "2 + x", "pi", "0")
try_function("cos-x", "cos(x)", "pi", "0")


print(cleanup(ddx("cos(x)")))
print(cleanup(ddx("x + x")))
