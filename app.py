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
# COMPACT MOBILE CSS
# ---------------------------------------------------------
st.markdown(
    """
<style>
.block-container {
    padding-top: 0.35rem !important;
    padding-bottom: 0.8rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 700px !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

[data-testid="stElementContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

hr {
    margin-top: 0.35rem !important;
    margin-bottom: 0.35rem !important;
}

[data-testid="stAlert"] {
    margin-top: 0.15rem !important;
    margin-bottom: 0.15rem !important;
}

[data-testid="stSelectbox"],
[data-testid="stNumberInput"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

iframe {
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}
</style>
""",
    unsafe_allow_html=True
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
# SCANNER COMPONENT
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

if "entry_counter" not in st.session_state:
    st.session_state.entry_counter = 0

if "reset_token" not in st.session_state:
    st.session_state.reset_token = 0

if "saved_message" not in st.session_state:
    st.session_state.saved_message = False


# ---------------------------------------------------------
# ΜΗΝΥΜΑ ΑΠΟΘΗΚΕΥΣΗΣ
# ---------------------------------------------------------
if st.session_state.saved_message:

    st.success("✅ Η τιμή αποθηκεύτηκε!")

    st.session_state.saved_message = False


# ---------------------------------------------------------
# SCANNER
# ---------------------------------------------------------
barcode_result = barcode_scanner(
    reset_token=st.session_state.reset_token,
    key="barcode_scanner_main",
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

            st.success("✅ Το προϊόν αναγνωρίστηκε!")

        else:

            st.session_state.current_barcode = None

            st.error(
                f"⛔ Το barcode {barcode} δεν υπάρχει στη λίστα προϊόντων."
            )


# ---------------------------------------------------------
# ΠΡΟΪΟΝ + MARKET + ΤΙΜΗ
# ---------------------------------------------------------
if st.session_state.current_barcode:

    barcode = st.session_state.current_barcode
    product = PRODUCTS[barcode]

    product_card = f"""
<div style="
    margin:4px 0 6px 0;
    padding:10px 12px;
    border-radius:12px;
    background:#f7f7f9;
">
    <div style="
        font-size:15px;
        font-weight:600;
        margin-bottom:3px;
    ">
        🛒 Προϊόν
    </div>

    <div style="
        font-size:21px;
        font-weight:700;
        line-height:1.2;
        margin-bottom:4px;
    ">
        {product}
    </div>

    <div style="
        font-size:13px;
        opacity:0.75;
    ">
        Barcode: {barcode}
    </div>
</div>
"""

    st.markdown(
        product_card,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # MARKET
    # -----------------------------------------------------
    market = st.selectbox(
        "🏪 Market",
        MARKETS,
        index=0,
        key=f"market_{st.session_state.entry_counter}"
    )


    # -----------------------------------------------------
    # ΤΙΜΗ
    # -----------------------------------------------------
    price = st.number_input(
        "💶 Τιμή (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f",
        key=f"price_{st.session_state.entry_counter}"
    )


    # -----------------------------------------------------
    # ΑΠΟΘΗΚΕΥΣΗ
    # -----------------------------------------------------
    if st.button(
        "💾 Αποθήκευση τιμής",
        type="primary",
        use_container_width=True
    ):

        if price <= 0:

            st.warning("⚠️ Γράψε πρώτα την τιμή.")

        else:

            now = datetime.now()

            st.session_state.records.append(
                {
                    "Ημερομηνία": now.strftime("%d/%m/%Y"),
                    "Ώρα": now.strftime("%H:%M"),
                    "Market": market,
                    "Barcode": barcode,
                    "Προϊόν": product,
                    "Τιμή": price,
                }
            )

            st.session_state.current_barcode = None
            st.session_state.last_barcode = None

            st.session_state.entry_counter += 1
            st.session_state.reset_token += 1

            st.session_state.saved_message = True

            st.rerun()


# ---------------------------------------------------------
# ΚΑΤΑΧΩΡΗΣΕΙΣ
# ---------------------------------------------------------
if st.session_state.records:

    st.markdown("### 📋 Καταχωρήσεις")

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
