from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.xlsx")
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.xlsx")


def load_customers():
    df = pd.read_excel(CUSTOMERS_FILE)
    df.columns = df.columns.str.strip()
    return df


def load_products():
    df = pd.read_excel(PRODUCTS_FILE)
    df.columns = df.columns.str.strip()
    return df


@app.route("/")
def index():
    customers = load_customers()

    lines = (
        customers["لاین"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return render_template("step1.html", lines=lines)


@app.route("/get_routes")
def get_routes():
    line = request.args.get("line")
    customers = load_customers()

    routes = (
        customers[customers["لاین"].astype(str) == str(line)]["عنوان مسیر"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    routes.sort()
    return jsonify(routes)


@app.route("/get_customers")
def get_customers():
    route = request.args.get("route")
    customers = load_customers()

    result = customers[
        customers["عنوان مسیر"].astype(str) == str(route)
    ][["نام", "تارگت ریالی نهایی"]]

    return jsonify(result.fillna("").to_dict("records"))


@app.route("/products")
def products():

    customer = request.args.get("customer")

    customers = load_customers()
    products = load_products()

    customers = customers.fillna("")
    products = products.fillna("")

    row = customers[customers["نام"].astype(str) == str(customer)]

    target = 0
    if not row.empty:
        target = float(row.iloc[0]["تارگت ریالی نهایی"] or 0)

    grouped = {}

    for _, r in products.iterrows():
        brand = str(r.get("برند", "")).strip()
        grouped.setdefault(brand, []).append(r.to_dict())

    return render_template(
        "step2.html",
        customer=customer,
        grouped_products=grouped,
        target=target
    )


@app.route("/summary")
def summary():
    return render_template("step3.html")

@app.route("/submit", methods=["POST"])
def submit():

    try:

        data = request.get_json()

        customer = data.get("customer")
        items = data.get("items", [])

        customers = load_customers()
        products = load_products()

        customers = customers.fillna("")
        products = products.fillna("")

        c_row = customers[customers["نام"].astype(str) == str(customer)]

        customer_code = ""
        if not c_row.empty:
            customer_code = str(c_row.iloc[0].get("کد مشتری", ""))

        order_items = []
        total = 0

        for i in items:

            qty = int(i.get("qty", 0))
            price = float(i.get("price", 0))
            title = i.get("title", "")

            if qty <= 0:
                continue

            p_row = products[products["عنوان محصول"] == title]

            product_code = ""
            brand = ""

            if not p_row.empty:
                product_code = str(p_row.iloc[0].get("کد محصول", ""))
                brand = str(p_row.iloc[0].get("برند", ""))

            row_total = qty * price
            total += row_total

            # ✅ این باید داخل loop باشد
            order_items.append({
                "title": title,
                "brand": brand,
                "qty": qty,
                "total": row_total
            })

        return jsonify({
            "status": "ok",
            "customer": customer,
            "items": order_items,
            "total": total,
            "rows": len(order_items),
            "qty": sum(x["qty"] for x in order_items)
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)