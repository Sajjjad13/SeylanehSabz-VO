from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# =========================
# PATHS (GitHub / Render SAFE)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.xlsx")
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.xlsx")


# =========================
# LOADERS (SAFE)
# =========================
def load_customers():
    try:
        df = pd.read_excel(CUSTOMERS_FILE)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print("CUSTOMERS LOAD ERROR:", e)
        return pd.DataFrame()


def load_products():
    try:
        df = pd.read_excel(PRODUCTS_FILE)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print("PRODUCTS LOAD ERROR:", e)
        return pd.DataFrame()


# =========================
# STEP 1
# =========================
@app.route("/")
def index():
    customers = load_customers()

    if customers.empty:
        return "Customers file not found or empty"

    lines = (
        customers["لاین"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    return render_template("step1.html", lines=lines)


# =========================
# ROUTES
# =========================
@app.route("/get_routes")
def get_routes():
    line = request.args.get("line")
    customers = load_customers()

    if customers.empty:
        return jsonify([])

    routes = (
        customers[customers["لاین"].astype(str) == str(line)]["عنوان مسیر"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    routes.sort()
    return jsonify(routes)


# =========================
# CUSTOMERS
# =========================
@app.route("/get_customers")
def get_customers():
    route = request.args.get("route")
    customers = load_customers()

    if customers.empty:
        return jsonify([])

    result = customers[
        customers["عنوان مسیر"].astype(str) == str(route)
    ][["نام", "تارگت ریالی نهایی"]]

    return jsonify(result.fillna("").to_dict("records"))


# =========================
# STEP 2
# =========================
@app.route("/products")
def products_page():
    customer = request.args.get("customer")

    customers = load_customers()
    products_df = load_products()

    if customers.empty or products_df.empty:
        return "Data missing"

    customers = customers.fillna("")
    products_df = products_df.fillna("")

    row = customers[customers["نام"].astype(str) == str(customer)]

    target = 0
    if not row.empty:
        target = float(row.iloc[0].get("تارگت ریالی نهایی") or 0)

    grouped = {}

    for _, r in products_df.iterrows():
        brand = str(r.get("برند", "")).strip()
        grouped.setdefault(brand, []).append(r.to_dict())

    return render_template(
        "step2.html",
        customer=customer,
        grouped_products=grouped,
        target=target
    )


# =========================
# STEP 3
# =========================
@app.route("/summary")
def summary():
    return render_template("step3.html")


# =========================
# SUBMIT ORDER (FULL FIXED)
# =========================
@app.route("/submit", methods=["POST"])
def submit():

    try:
        data = request.get_json()

        customer = data.get("customer")
        items = data.get("items", [])

        customers = load_customers()
        products_df = load_products()

        if customers.empty or products_df.empty:
            return jsonify({"status": "error", "message": "data missing"}), 500

        customers = customers.fillna("")
        products_df = products_df.fillna("")

        c_row = customers[customers["نام"].astype(str) == str(customer)]

        customer_code = ""
        if not c_row.empty:
            customer_code = str(c_row.iloc[0].get("کد مشتری", ""))

        order_items = []
        total = 0
        total_qty = 0

        for i in items:

            # =========================
            # SAFE CONVERT
            # =========================
            try:
                qty = int(float(i.get("qty") or 0))
                price = float(i.get("price") or 0)
            except:
                continue

            title = str(i.get("title", "")).strip()

            if qty <= 0 or title == "":
                continue

            # =========================
            # FIND PRODUCT
            # =========================
            p_row = products_df[
                products_df["عنوان محصول"].astype(str).str.strip() == title
            ]

            brand = ""
            product_code = ""

            if not p_row.empty:
                brand = str(p_row.iloc[0].get("برند", ""))
                product_code = str(p_row.iloc[0].get("کد محصول", ""))

            row_total = qty * price

            total += row_total
            total_qty += qty

            # =========================
            # APPEND ITEM (FIXED)
            # =========================
            order_items.append({
                "title": title,
                "brand": brand,
                "qty": qty,
                "price": price,
                "total": row_total
            })

        return jsonify({
            "status": "ok",
            "customer": customer,
            "customer_code": customer_code,
            "items": order_items,
            "total": total,
            "rows": len(order_items),
            "qty": total_qty
        })

    except Exception as e:
        print("FATAL ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
