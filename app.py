from flask import Flask, jsonify, request
import sqlite3
import os
from collections import OrderedDict

app = Flask(__name__)

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "API Historico conectada correctamente ✅"}

@app.route('/ventas_detalle', methods=['GET'])
def ventas_detalle():
    nit = request.args.get("nit")
    cliente = request.args.get("cliente")  # nombre parcial del cliente
    busqueda_ref = request.args.get("busqueda_ref")  # texto parcial como 'fs 30015'

    if not (nit or cliente) or not busqueda_ref:
        return jsonify({"error": "Debe enviar 'nit' o 'cliente', y 'busqueda_ref' para la referencia o nombre del producto"}), 400

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
            WHERE ({cond_cliente}) AND (referencia LIKE ? OR descripcion LIKE ?)
            ORDER BY fecha DESC
        """

        params = []
        if nit:
            cond_cliente = "nit = ?"
            params.append(nit)
        else:
            cond_cliente = "LOWER(display_name) LIKE ?"
            params.append(f"%{cliente.lower()}%")

        params.extend([f"%{busqueda_ref}%", f"%{busqueda_ref}%"])
        cursor.execute(query.format(cond_cliente=cond_cliente), params)

        rows = cursor.fetchall()
        agrupado = {}
        for row in rows:
            etiqueta = f"{row['display_name']} / {row['sucursal']}"
            if etiqueta not in agrupado:
                agrupado[etiqueta] = []

            fecha_corta = row['fecha'].split(" ")[0]

            agrupado[etiqueta].append(OrderedDict([
                ("price_unit", row['price_unit']),
                ("cantidad", row['cantidad']),
                ("producto", row['producto']),
                ("fecha", fecha_corta),
                ("factura", row['factura']),
                ("total_venta", round(float(row['price_unit']) * float(row['cantidad']), 2))
            ]))

        return jsonify(agrupado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 🔁 Esto permite que Render detecte correctamente el puerto
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
