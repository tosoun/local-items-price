import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from io import BytesIO
from datetime import datetime
import base64

from supabase import create_client


# ---------------------------------------------------------
# ΡΥΘΜΙΣΕΙΣ
# ---------------------------------------------------------
st.set_page_config(
    page_title="Καταγραφή Τιμών",
    page_icon="📱",
    layout="centered"
)


# ---------------------------------------------------------
# SUPABASE
# ---------------------------------------------------------
@st.cache_resource
def get_supabase():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


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

.excel-button {
    display: block;
    width: 100%;
    text-align: center;
    padding: 12px 16px;
    margin-top: 8px;

    background: #ffffff;
    color: #111827 !important;

    border: 1px solid #d1d5db;
    border-radius: 8px;

    font-size: 16px;
    font-weight: 600;

    text-decoration: none !important;
}

.excel-button:hover {
    background: #f3f4f6;
}

</style>
""",
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# ΠΡΟΪΟΝΤΑ
# ---------------------------------------------------------
PRODUCTS = {
    "5200120690012": "ΘΕΟΝΗ – Φυσικό Μεταλλικό Νερό 0,5λ",
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

if "manual_search_message" not in st.session_state:
    st.session_state.manual_search_message = ""


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
# ΕΛΕΓΧΟΣ BARCODE ΑΠΟ SCANNER
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


        # -------------------------------------------------
        # ΤΟ ΠΡΟΪΟΝ ΔΕΝ ΥΠΑΡΧΕΙ
        # -------------------------------------------------
        else:

            st.session_state.current_barcode = None

            st.session_state.scanner_message = (
                "⛔ Ο κωδικός δεν υπάρχει"
            )

            st.session_state.reset_token += 1

            st.rerun()


# ---------------------------------------------------------
# ΧΕΙΡΟΚΙΝΗΤΗ ΑΝΑΖΗΤΗΣΗ BARCODE
# ---------------------------------------------------------
st.markdown(
    "### 🔎 Χειροκίνητη αναζήτηση"
)


manual_barcode = st.text_input(
    "Barcode προϊόντος",
    placeholder="Πληκτρολόγησε το barcode",
    key="manual_barcode_input"
)


if st.button(
    "🔎 Αναζήτηση προϊόντος",
    use_container_width=True
):

    code = manual_barcode.strip()


    # -----------------------------------------------------
    # ΔΕΝ ΓΡΑΦΤΗΚΕ ΚΩΔΙΚΟΣ
    # -----------------------------------------------------
    if not code:

        st.session_state.manual_search_message = (
            "⚠️ Πληκτρολόγησε πρώτα ένα barcode."
        )


    # -----------------------------------------------------
    # ΒΡΕΘΗΚΕ ΠΡΟΪΟΝ
    # -----------------------------------------------------
    elif code in PRODUCTS:

        st.session_state.current_barcode = code

        st.session_state.manual_search_message = (
            "✅ Το προϊόν βρέθηκε."
        )

        st.rerun()


    # -----------------------------------------------------
    # ΔΕΝ ΒΡΕΘΗΚΕ
    # -----------------------------------------------------
    else:

        st.session_state.current_barcode = None

        st.session_state.manual_search_message = (
            "⛔ Ο κωδικός δεν υπάρχει στη βάση προϊόντων."
        )

        st.rerun()


# ---------------------------------------------------------
# ΜΗΝΥΜΑ ΧΕΙΡΟΚΙΝΗΤΗΣ ΑΝΑΖΗΤΗΣΗΣ
# ---------------------------------------------------------
if st.session_state.manual_search_message:

    message = (
        st.session_state.manual_search_message
    )

    if message.startswith("✅"):

        st.success(
            message
        )

    elif message.startswith("⛔"):

        st.warning(
            message
        )

    else:

        st.info(
            message
        )

    st.session_state.manual_search_message = ""


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


            # -------------------------------------------------
            # ΑΠΟΘΗΚΕΥΣΗ ΣΤΟ SUPABASE
            # -------------------------------------------------
            try:

                supabase.table(
                    "price_records"
                ).insert(
                    {
                        "market": market,
                        "barcode": barcode,
                        "product": product,
                        "price": float(price),
                    }
                ).execute()


                # -------------------------------------------------
                # ΤΟΠΙΚΗ ΚΑΤΑΧΩΡΗΣΗ
                # -------------------------------------------------
                st.session_state.records.append(
                    {
                        "Ημερομηνία":
                            now.strftime(
                                "%d/%m/%Y"
                            ),

                        "Ώρα":
                            now.strftime(
                                "%H:%M"
                            ),

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

                st.session_state.scanner_message = ""

                st.session_state.reset_token += 1

                st.session_state.saved_message = True

                st.rerun()


            except Exception as e:

                st.error(
                    "❌ Δεν έγινε αποθήκευση στη βάση."
                )

                st.caption(
                    str(e)
                )


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
    # ΔΗΜΙΟΥΡΓΙΑ EXCEL
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


    excel_data = (
        output.getvalue()
    )


    excel_base64 = (
        base64.b64encode(
            excel_data
        ).decode(
            "utf-8"
        )
    )


    # -----------------------------------------------------
    # EXCEL ΣΕ ΝΕΑ ΚΑΡΤΕΛΑ
    # -----------------------------------------------------
    excel_href = (
        "data:"
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet;base64,"
        +
        excel_base64
    )


    excel_button = (
        f'<a class="excel-button" '
        f'href="{excel_href}" '
        f'download="local_items_prices.xlsx" '
        f'target="_blank" '
        f'rel="noopener noreferrer">'
        f'📥 Άνοιγμα / Κατέβασμα Excel'
        f'</a>'
    )


    st.markdown(
        excel_button,
        unsafe_allow_html=True
    )
