from flask import Flask
import os

app = Flask(__name__)

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "API Historico conectada correctamente ✅"}

@app.route('/ventas_detalle', methods=['GET'])
def ventas_detalle():
    nit = request.args.get("nit")
    referencia = request.args.get("referencia")

    if not nit or not referencia:
        return jsonify({"error": "Parámetros 'nit' y 'referencia' son obligatorios"}), 400

    try:
        conn = sqlite3.connect('historico.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                sucursal,
                referencia || ' - ' || descripcion AS producto,
                price_unit,
                cantidad,
                fecha,
                factura,
                display_name
            FROM ventas
            WHERE nit = ? AND referencia = ?
            ORDER BY fecha DESC
        """
        cursor.execute(query, (nit, referencia))
        rows = cursor.fetchall()

        # Agrupar por sucursal
        agrupado = {}
        for row in rows:
            sucursal = row['sucursal']
            etiqueta = f"{row['display_name']} / {sucursal}"

            if etiqueta not in agrupado:
                agrupado[etiqueta] = []

            agrupado[etiqueta].append({
                "producto": row['producto'],
                "price_unit": row['price_unit'],
                "cantidad": row['cantidad'],
                "fecha": row['fecha'],
                "factura": row['factura']
            })

        return jsonify(agrupado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 🔁 Esto permite que Render detecte correctamente el puerto
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
