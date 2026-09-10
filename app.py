import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from io import BytesIO
from datetime import datetime


# ---------------------------------------------------------
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# ---------------------------------------------------------
st.set_page_config(
    page_title="Καταγραφή Τιμών",
    page_icon="📱",
    layout="centered"
)


# ---------------------------------------------------------
# ΠΡΟΪΟΝΤΑ
# ---------------------------------------------------------
PRODUCTS = {
    "5200120690012": "ΘΕΟΝΗ – Φυσικό Μεταλλικό Νερό",
}


# ---------------------------------------------------------
# MARKETS
# ---------------------------------------------------------
MARKETS = [
    "Μασούτης",
    "Σκλαβενίτης",
    "ΑΒ Βασιλόπουλος",
    "My market",
    "Γαλαξίας",
    "Market In",
]


# ---------------------------------------------------------
# CUSTOM SCANNER
# ---------------------------------------------------------
barcode_scanner = components.declare_component(
    "barcode_scanner",
    path="scanner_component"
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "records" not in st.session_state:
    st.session_state.records = []

if "current_barcode" not in st.session_state:
    st.session_state.current_barcode = None

if "last_barcode" not in st.session_state:
    st.session_state.last_barcode = None

if "scanner_counter" not in st.session_state:
    st.session_state.scanner_counter = 0

if "entry_counter" not in st.session_state:
    st.session_state.entry_counter = 0


# ---------------------------------------------------------
# ΤΙΤΛΟΣ
# ---------------------------------------------------------
st.title("📱 Καταγραφή Τιμών")

st.caption(
    "Σκάναρε το barcode του προϊόντος και καταχώρησε market και τιμή."
)


# ---------------------------------------------------------
# SCANNER
# ---------------------------------------------------------
st.subheader("📷 Scanner")

barcode_result = barcode_scanner(
    key=f"barcode_scanner_{st.session_state.scanner_counter}",
    default=None
)


# ---------------------------------------------------------
# ΕΛΕΓΧΟΣ BARCODE
# ---------------------------------------------------------
if barcode_result:

    barcode = str(barcode_result).strip()

    if barcode != st.session_state.last_barcode:

        st.session_state.last_barcode = barcode

        if barcode in PRODUCTS:

            st.session_state.current_barcode = barcode

            st.success(
                "✅ Το προϊόν αναγνωρίστηκε!"
            )

        else:

            st.session_state.current_barcode = None

            st.error(
                f"⛔ Το barcode {barcode} "
                "δεν υπάρχει στη λίστα προϊόντων."
            )


# ---------------------------------------------------------
# ΠΡΟΪΟΝ + MARKET + ΤΙΜΗ
# ---------------------------------------------------------
if st.session_state.current_barcode:

    barcode = st.session_state.current_barcode
    product = PRODUCTS[barcode]

    st.divider()

    st.subheader("🛒 Προϊόν")

    st.markdown(
        f"### {product}"
    )

    st.write(
        f"**Barcode:** {barcode}"
    )


    market = st.selectbox(
        "🏪 Επιλογή Market",
        MARKETS,
        key=f"market_{st.session_state.entry_counter}"
    )


    price = st.number_input(
        "💶 Τιμή (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f",
        key=f"price_{st.session_state.entry_counter}"
    )


    if st.button(
        "💾 Αποθήκευση τιμής",
        type="primary",
        use_container_width=True
    ):

        if price <= 0:

            st.warning(
                "⚠️ Γράψε πρώτα την τιμή."
            )

        else:

            now = datetime.now()

            st.session_state.records.append(
                {
                    "Ημερομηνία":
                        now.strftime("%d/%m/%Y"),

                    "Ώρα":
                        now.strftime("%H:%M"),

                    "Market":
                        market,

                    "Barcode":
                        barcode,

                    "Προϊόν":
                        product,

                    "Τιμή":
                        price,
                }
            )

            st.session_state.current_barcode = None
            st.session_state.last_barcode = None

            st.session_state.entry_counter += 1
            st.session_state.scanner_counter += 1

            st.success(
                "✅ Η τιμή αποθηκεύτηκε."
            )

            st.rerun()


# ---------------------------------------------------------
# ΚΑΤΑΧΩΡΗΣΕΙΣ
# ---------------------------------------------------------
if st.session_state.records:

    st.divider()

    st.subheader("📋 Καταχωρήσεις")

    df = pd.DataFrame(
        st.session_state.records
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Τιμές"
        )


    st.download_button(
        label="📥 Κατέβασμα Excel",
        data=output.getvalue(),
        file_name="local_items_prices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
