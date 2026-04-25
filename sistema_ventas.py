import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Mundo Fiesta On Line",
    page_icon="apple-touch-icon.png",
    layout="wide"
)
st.markdown("""
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Mundo Fiesta">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0b1020">
""", unsafe_allow_html=True)
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    max-width: 1200px;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827, #1f2937);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #334155;
}

[data-testid="stForm"] {
    background: #111827;
    padding: 24px;
    border-radius: 20px;
    border: 1px solid #334155;
}

.stButton button {
    background: linear-gradient(90deg, #dc2626, #f59e0b);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 700;
}

.stDownloadButton button {
    background: #1d4ed8;
    color: white;
    border-radius: 12px;
    border: none;
}
</style>
""", unsafe_allow_html=True)
#  HEADER PRO
col1, col2 = st.columns([1, 5])

with col1:
    st.image("Logo Mundo sin fondo_page-0001.png", width=100)

with col2:
    st.markdown("""
    <h1 style="margin-bottom:0;">Sistema de Ventas Online</h1>
    <h3 style="margin-top:0; color:#facc15;">Mundo Fiesta · Callbell</h3>
    <p style="color:#cbd5e1;">Control de ventas online, pagos, envíos y comisiones.</p>
    """, unsafe_allow_html=True)

st.markdown("---")

from datetime import date
# 🔗 Conexión a Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = dict(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Ventas Callbell").get_worksheet(0)
def cargar_datos():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = cargar_datos()


st.title("🎉 Sistema de Ventas - Mundo Fiesta")

df = cargar_datos()

if df.empty:
    df = pd.DataFrame(columns=[
        "Factura", "Importe", "Cliente", "Ciudad", "Fecha",
        "Envio", "FormaPago", "PagoConfirmado",
        "Vendedor", "PreparadoPor", "EnviadoPor", "VerificadoPor"
    ])

if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.date
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)

# ---------------- NUEVA VENTA ----------------
st.subheader("➕ Nueva Venta")

with st.form("form_venta"):
    col1, col2, col3 = st.columns(3)

    with col1:
        factura = st.text_input("N° Factura")
        cliente = st.text_input("Cliente")
        ciudad = st.text_input("Ciudad")

    with col2:
        fecha = st.date_input("Fecha", date.today())
        importe = st.number_input("Importe", min_value=0.0, step=1000.0)

    with col3:
        envio = st.selectbox("Medio de envío", ["Retiro en tienda", "Transportadora", "Moto Bolt", "Otro"])
        forma_pago = st.selectbox("Forma de pago", ["QR", "Tarjeta", "Transferencia", "Efectivo"])
        pago_confirmado = st.selectbox("Pago confirmado", ["SI", "NO"])

    col4, col5 = st.columns(2)

    with col4:
        vendedor = st.selectbox("Vendedor", ["Coinda", "Diana", "Leticia", "Otro"])
        preparado = st.selectbox("Preparado por", ["Coinda", "Diana", "Leticia", "Otro"])

    with col5:
        enviado = st.selectbox("Enviado por", ["Retiro en Tienda", "Transportadora", "Moto Bolt", "Otro"])
        verificado = st.text_input("Verificado por", value="Don Hugo")

    guardar = st.form_submit_button("Guardar venta")

    if guardar:
        nueva = {
            "Factura": factura,
            "Importe": importe,
            "Cliente": cliente,
            "Ciudad": ciudad,
            "Fecha": fecha,
            "Envio": envio,
            "FormaPago": forma_pago,
            "PagoConfirmado": pago_confirmado,
            "Vendedor": vendedor,
            "PreparadoPor": preparado,
            "EnviadoPor": enviado,
            "VerificadoPor": verificado
        }

        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
        sheet.append_row([
    factura,
    importe,
    cliente,
    ciudad,
    str(fecha),
    envio,
    forma_pago,
    pago_confirmado,
    vendedor,
    preparado,
    enviado,
    verificado
])
        df = cargar_datos()
        st.success("✅ Venta registrada")
        st.rerun()

# ---------------- FILTROS ----------------
st.subheader("🔍 Filtros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    fecha_desde = st.date_input("Desde", df["Fecha"].min() if not df.empty else date.today())

with col2:
    fecha_hasta = st.date_input("Hasta", df["Fecha"].max() if not df.empty else date.today())

with col3:
    vendedores = df["Vendedor"].dropna().astype(str).str.strip().unique().tolist()
vendedores = sorted([v for v in vendedores if v != ""])

vendedor_filtro = st.selectbox(
    "Vendedor",
    ["Todos", "Coinda", "Diana", "Leticia", "Otro"]
)

with col4:
    pago_filtro = st.selectbox(
        "Pago confirmado",
        ["Todos", "SI", "NO"]
    )

df_filtrado = df.copy()

if not df_filtrado.empty:
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_desde) &
        (df_filtrado["Fecha"] <= fecha_hasta)
    ]

if vendedor_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Vendedor"] == vendedor_filtro]

if pago_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["PagoConfirmado"] == pago_filtro]

# ---------------- DASHBOARD ----------------
st.subheader("📈 Dashboard")

total = df_filtrado["Importe"].sum() if not df_filtrado.empty else 0
cantidad = len(df_filtrado)
ticket_promedio = total / cantidad if cantidad > 0 else 0
pendientes = len(df_filtrado[df_filtrado["PagoConfirmado"] == "NO"]) if not df_filtrado.empty else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total vendido", f"Gs. {total:,.0f}")
col2.metric("🧾 Cantidad ventas", cantidad)
col3.metric("🎯 Ticket promedio", f"Gs. {ticket_promedio:,.0f}")
col4.metric("⚠️ Pagos pendientes", pendientes)

if not df_filtrado.empty:
    st.subheader("Ventas por vendedor")
    ventas_vendedor = df_filtrado.groupby("Vendedor")["Importe"].sum().reset_index()
    st.bar_chart(ventas_vendedor, x="Vendedor", y="Importe")
# ---------------- CIERRE DE COMISIONES ----------------
st.subheader("💰 Cierre de comisiones")

porcentaje_comision = 0.0075

if not df_filtrado.empty:
    cierre = df_filtrado.groupby("Vendedor")["Importe"].sum().reset_index()
    cierre["Comisión 0.75%"] = cierre["Importe"] * porcentaje_comision

    st.dataframe(cierre, use_container_width=True)

    total_comisiones = cierre["Comisión 0.75%"].sum()

    st.metric("Total a pagar en comisiones", f"Gs. {total_comisiones:,.0f}")

    csv_comisiones = cierre.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Descargar cierre de comisiones",
        data=csv_comisiones,
        file_name="cierre_comisiones.csv",
        mime="text/csv"
    )
else:
    st.info("No hay ventas para calcular comisiones.")

# ---------------- TABLA EDITABLE ----------------
st.subheader("📊 Ventas cargadas")

df_editado = st.data_editor(
    df_filtrado,
    use_container_width=True,
    num_rows="dynamic"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Guardar cambios editados"):
        st.success("✅ Cambios guardados")
        st.rerun()

with col2:
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name="ventas_filtradas.csv",
        mime="text/csv"
    )

# ---------------- ELIMINAR ----------------
st.subheader("🗑️ Eliminar venta")

if not df.empty:
    factura_eliminar = st.selectbox(
        "Elegí la factura a eliminar",
        df["Factura"].astype(str).tolist()
    )

    if st.button("Eliminar venta"):
        # Buscar la fila real en Google Sheets
        facturas_sheet = sheet.col_values(1)  # Columna A = Factura

        fila_a_eliminar = None

        for indice, factura in enumerate(facturas_sheet, start=1):
            if str(factura) == str(factura_eliminar):
                fila_a_eliminar = indice
                break

        if fila_a_eliminar:
            sheet.delete_rows(fila_a_eliminar)
            st.success("✅ Venta eliminada de Google Sheets")
            st.rerun()
        else:
            st.error("❌ No se encontró esa factura en Google Sheets")
else:
    st.info("Todavía no hay ventas cargadas.")