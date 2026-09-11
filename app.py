import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from io import BytesIO
from datetime import datetime


# ---------------------------------------------------------
# ΡΥΘΜΙΣΕΙΣ
# ---------------------------------------------------------
st.set_page_config(
    page_title="Καταγραφή Τιμών",
    page_icon="📱",
    layout="centered"
)


# ---------------------------------------------------------
# ΜΙΚΡΑ ΚΕΝΑ
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 1rem !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    div[data-testid="stAlert"] {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }

    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    iframe {
        display: block !important;
        margin: 0 !important;
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

if "last_scan_id" not in st.session_state:
    st.session_state.last_scan_id = None

if "entry_counter" not in st.session_state:
    st.session_state.entry_counter = 0

if "reset_token" not in st.session_state:
    st.session_state.reset_token = 0

if "saved_message" not in st.session_state:
    st.session_state.saved_message = False

if "scanner_message" not in st.session_state:
    st.session_state.scanner_message = ""


# ---------------------------------------------------------
# ΜΗΝΥΜΑ ΑΠΟΘΗΚΕΥΣΗΣ
# ---------------------------------------------------------
if st.session_state.saved_message:

    st.success(
        "✅ Η τιμή αποθηκεύτηκε!"
    )

    st.session_state.saved_message = False


# ---------------------------------------------------------
# SCANNER
# ---------------------------------------------------------
barcode_result = barcode_scanner(
    reset_token=st.session_state.reset_token,
    scanner_message=st.session_state.scanner_message,
    key="barcode_scanner_main",
    default=None
)


# Το μήνυμα έχει ήδη σταλεί στον scanner
st.session_state.scanner_message = ""


# ---------------------------------------------------------
# ΕΛΕΓΧΟΣ BARCODE
# ---------------------------------------------------------
if barcode_result:

    if isinstance(
        barcode_result,
        dict
    ):

        barcode = str(
            barcode_result.get(
                "code",
                ""
            )
        ).strip()

        scan_id = barcode_result.get(
            "scan_id"
        )

    else:

        barcode = str(
            barcode_result
        ).strip()

        scan_id = barcode


    # -----------------------------------------------------
    # ΝΕΟ SCAN
    # -----------------------------------------------------
    if (
        scan_id !=
        st.session_state.last_scan_id
    ):

        st.session_state.last_scan_id = scan_id


        # -------------------------------------------------
        # ΤΟ ΠΡΟΪΟΝ ΥΠΑΡΧΕΙ
        # -------------------------------------------------
        if barcode in PRODUCTS:

            st.session_state.current_barcode = barcode

            st.success(
                "✅ Το προϊόν αναγνωρίστηκε!"
            )


        # -------------------------------------------------
        # ΤΟ ΠΡΟΪΟΝ ΔΕΝ ΥΠΑΡΧΕΙ
        # -------------------------------------------------
        else:

            st.session_state.current_barcode = None

            # Μήνυμα μέσα στον scanner
            st.session_state.scanner_message = (
                "⛔ Ο κωδικός δεν υπάρχει"
            )

            # Restart scanner
            st.session_state.reset_token += 1

            st.rerun()


# ---------------------------------------------------------
# ΠΡΟΪΟΝ + MARKET + ΤΙΜΗ
# ---------------------------------------------------------
if st.session_state.current_barcode:

    barcode = (
        st.session_state.current_barcode
    )

    product = PRODUCTS[
        barcode
    ]


    st.markdown(
        "### 🛒 Προϊόν"
    )

    st.markdown(
        f"**{product}**"
    )

    st.caption(
        f"Barcode: {barcode}"
    )


    # -----------------------------------------------------
    # MARKET
    # -----------------------------------------------------
    market = st.selectbox(
        "🏪 Market",
        MARKETS,
        index=0,
        key=(
            f"market_"
            f"{st.session_state.entry_counter}"
        )
    )


    # -----------------------------------------------------
    # ΤΙΜΗ
    # -----------------------------------------------------
    price = st.number_input(
        "💶 Τιμή (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f",
        key=(
            f"price_"
            f"{st.session_state.entry_counter}"
        )
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

            st.session_state.entry_counter += 1

            # Κανονικό restart scanner
            st.session_state.scanner_message = ""

            st.session_state.reset_token += 1

            st.session_state.saved_message = True

            st.rerun()


# ---------------------------------------------------------
# ΚΑΤΑΧΩΡΗΣΕΙΣ
# ---------------------------------------------------------
if st.session_state.records:

    st.markdown(
        "### 📋 Καταχωρήσεις"
    )

    df = pd.DataFrame(
        st.session_state.records
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # EXCEL
    # -----------------------------------------------------
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
        mime=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )
