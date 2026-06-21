import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

x = sp.Symbol('x')

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse(s):
    return parse_expr(s, transformations=TRANSFORMATIONS, evaluate=True)


# ---------------- UI ----------------
st.markdown(
    "<span style='color:red; font-size:24px;'>Mini Maths Calculator</span>",
    unsafe_allow_html=True,
)

user_input = st.text_input("Function")

choice = st.selectbox(
    "Operation",
    [
        "Integration",
        "Differentiation",
        "Solving equation for x",
        "Factorising",
        "Plot a graph",
        "Expand brackets",
    ],
)

if not user_input:
    st.warning("Please enter a function first")
    st.stop()

user_input = user_input.strip()

# ✅ FIX 1: safe parsing (stop immediately if invalid)
try:
    expr = parse(user_input)
except Exception as e:
    st.error(f"Invalid function: {e}")
    st.stop()


# ---------------- INTEGRATION ----------------
if choice == "Integration":
    try:
        result = sp.integrate(expr, x)

        if isinstance(result, sp.Integral):
            st.write("Cannot be integrated in elementary form")
            st.latex(sp.latex(result))
        else:
            st.write("Integral:")
            st.latex(sp.latex(result) + " + C")

    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- DIFFERENTIATION ----------------
elif choice == "Differentiation":
    try:
        result = sp.diff(expr, x)

        st.write("Derivative:")
        st.latex(sp.latex(result))

    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- SOLVING EQUATION ----------------
elif choice == "Solving equation for x":
    try:
        cleaned = user_input.replace("==", "=")

        if "=" in cleaned:
            lhs, rhs = cleaned.split("=", 1)
            eq = sp.Eq(parse(lhs), parse(rhs))
        else:
            eq = sp.Eq(expr, 0)

        result = sp.solve(eq, x)

        if not result:
            st.write("No solutions found")
        else:
            st.write("Solutions:")
            for i, sol in enumerate(result, 1):
                st.latex(f"x_{{{i}}} = {sp.latex(sol)}")

    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- FACTORISING ----------------
elif choice == "Factorising":
    try:
        factored = sp.factor(expr)

        # FIX 2: more reliable comparison
        if sp.expand(factored) == sp.expand(expr):
            st.info("Cannot be factorised further")
            st.latex(sp.latex(expr))
        else:
            st.success("Factorised form:")
            st.latex(sp.latex(factored))

    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- GRAPH ----------------
elif choice == "Plot a graph":

    range_choice = st.selectbox(
        "Range of values of x",
        ["Small", "Medium", "Large", "Custom"]
    )

    if range_choice == "Small":
        xmin, xmax = -10, 10
    elif range_choice == "Medium":
        xmin, xmax = -50, 50
    elif range_choice == "Large":
        xmin, xmax = -500, 500
    else:
        xmin = st.number_input("Lower bound", value=-10, step=1)
        xmax = st.number_input("Upper bound", value=10, step=1)

    if xmin >= xmax:
        st.error("Lower bound must be less than upper bound")

    else:
        try:
            f = sp.lambdify(x, expr, "numpy")

            x_vals = np.linspace(xmin, xmax, 400)

            # FIX 3: safer numeric handling
            y_vals = np.array(f(x_vals), dtype=np.float64)
            y_vals = np.nan_to_num(y_vals, nan=np.nan, posinf=np.nan, neginf=np.nan)

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.axhline(0, color="black")
            ax.axvline(0, color="black")
            ax.set_title(f"y = {sp.latex(expr)}")

            st.pyplot(fig)

        except Exception as e:
            st.error(f"Graph error: {e}")


# ---------------- BINOMIAL EXPANSION ----------------
elif choice == "Expand brackets":
    try:
        expr = parse(user_input)

        # FORCE FULL EXPANSION
        expanded = sp.expand(expr, force=True)

        if expanded == expr:
            st.info("Expression is already expanded")
            st.latex(sp.latex(expr))
        else:
            st.success("Expanded form:")
            st.latex(sp.latex(expanded))

    except Exception as e:
        st.error(f"Error: {e}")
