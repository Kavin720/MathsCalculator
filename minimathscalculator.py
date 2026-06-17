import streamlit as st
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

x = sp.Symbol('x')

# Transformations let users type natural maths:
#   - implicit_multiplication_application: 2x, 2(x+1), x(x+1), (x+1)(x-1), xy
#   - convert_xor: allows ^ as power (e.g. x^2 becomes x**2)
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse(s):
    """Parse a user string into a SymPy expression, with friendly maths syntax."""
    return parse_expr(s, transformations=TRANSFORMATIONS, evaluate=True)


st.markdown(
    "<span style='color:red;'>Mini maths calculator</span>",
    unsafe_allow_html=True,
)

st.write(
    "Enter a function. You can use ^ or ** for powers, and implicit "
    "multiplication works (e.g. 2x, 2(x+1), (x+1)(x-1) are all fine)."
)

user_input = st.text_input("Function")

st.write("Which operation would you like to do?")

choice = st.selectbox(
    "Operation",
    ["Integration", "Differentiation", "Solving equation for x", "Factorising"],
)

if not user_input:
    st.warning("Please enter a function first")
    st.stop()

# Strip surrounding whitespace; the parser handles internal spacing itself.
user_input = user_input.strip()

if choice == "Integration":
    try:
        expr = parse(user_input)
        result = sp.integrate(expr, x)

        if isinstance(result, sp.Integral):
            st.write("Cannot be integrated in elementary form")
            st.latex(sp.latex(result))
        else:
            st.write("Integral:")
            st.latex(sp.latex(result) + " + C")

    except Exception as e:
        st.error(f"Invalid function: {e}")

elif choice == "Differentiation":
    try:
        expr = parse(user_input)
        result = sp.diff(expr, x)
        st.write("Derivative:")
        st.latex(sp.latex(result))

    except Exception as e:
        st.error(f"Invalid function: {e}")

elif choice == "Solving equation for x":
    try:
        # Normalise '==' to '=' so programming habits don't break things,
        # then split on the first '=' only.
        cleaned = user_input.replace("==", "=")
        if "=" in cleaned:
            lhs, rhs = cleaned.split("=", 1)
            eq = sp.Eq(parse(lhs), parse(rhs))
        else:
            eq = sp.Eq(parse(cleaned), 0)

        result = sp.solve(eq, x)

        if len(result) == 0:
            st.write("No solutions found")
        else:
            st.write("Solutions:")
            for i, sol in enumerate(result, 1):
                st.latex(f"x_{{{i}}} = {sp.latex(sol)}")

    except Exception as e:
        st.error(f"Invalid equation format: {e}")

elif choice == "Factorising":
    try:
        expr = parse(user_input)
        factored = sp.factor(expr)

        # Compare structurally: if factor() couldn't change the form,
        # it's already in simplest factored form.
        if factored == sp.expand(expr) or factored == expr:
            st.info("Cannot be factorised further (already simplest form)")
            st.latex(sp.latex(expr))
        else:
            st.success("Factorised form:")
            st.latex(sp.latex(factored))

    except Exception as e:
        st.error(f"Invalid expression: {e}")
