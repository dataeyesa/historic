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

@app.route('/ventas_busqueda_nombre', methods=['GET'])
def ventas_busqueda_nombre():
    cliente = request.args.get("cliente")
    producto = request.args.get("producto")

    if not cliente or not producto:
        return jsonify({"error": "Debe enviar los parámetros 'cliente' y 'producto'"}), 400

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
            WHERE LOWER(display_name) LIKE ? AND 
                  (LOWER(referencia) LIKE ? OR LOWER(descripcion) LIKE ?)
            ORDER BY fecha DESC
        """

        cliente_param = f"%{cliente.lower()}%"
        producto_param = f"%{producto.lower()}%"

        cursor.execute(query, (cliente_param, producto_param, producto_param))
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

        resultado_final = {
            "total_sucursales": len(agrupado),
            "resultados": agrupado
        }

        return jsonify(resultado_final)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 🔁 Esto permite que Render detecte correctamente el puerto
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
