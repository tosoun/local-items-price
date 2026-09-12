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
# CSS
# ---------------------------------------------------------
st.markdown(
    """
<style>

/* Κύριο περιεχόμενο */
.block-container {
    padding-top: 0.2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-bottom: 1rem !important;
}

/* Μικρότερα κενά */
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


/* -------------------------------------------------------
   STICKY MENU - Scanner / Τιμές
------------------------------------------------------- */
div[data-testid="stRadio"] {
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;

    background: rgba(255,255,255,0.98) !important;

    padding: 8px 6px 10px 6px !important;
    margin-top: 0 !important;
    margin-bottom: 8px !important;

    border-bottom: 1px solid #e5e7eb !important;

    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}


/* Κρατάμε τις επιλογές σε μία γραμμή */
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    gap: 18px !important;
    align-items: center !important;
}


/* Μέγεθος κειμένου menu */
div[data-testid="stRadio"] label {
    font-size: 17px !important;
    font-weight: 600 !important;
}


/* Excel button */
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
# ΕΠΙΛΟΓΗ ΣΕΛΙΔΑΣ
# ---------------------------------------------------------
page = st.radio(
    "",
    [
        "📷 Scanner",
        "📋 Τιμές"
    ],
    horizontal=True,
    label_visibility="collapsed"
)


# =========================================================
# ΣΕΛΙΔΑ ΤΙΜΩΝ
# =========================================================
if page == "📋 Τιμές":

    st.markdown("## 📋 Καταχωρημένες Τιμές")


    if st.button(
        "🔄 Ανανέωση",
        use_container_width=True
    ):
        st.rerun()


    try:

        response = (
            supabase
            .table("price_records")
            .select("*")
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )


        rows = response.data


        if not rows:

            st.info(
                "Δεν υπάρχουν ακόμη καταχωρήσεις."
            )


        else:

            df_prices = pd.DataFrame(rows)


            if "created_at" in df_prices.columns:

                df_prices["created_at"] = pd.to_datetime(
                    df_prices["created_at"],
                    utc=True,
                    errors="coerce"
                )

                df_prices["created_at"] = (
                    df_prices["created_at"]
                    .dt.tz_convert(
                        "Europe/Athens"
                    )
                )


            if "market" in df_prices.columns:

                markets_found = (
                    df_prices["market"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                market_options = [
                    "Όλα"
                ] + sorted(
                    markets_found
                )

            else:

                market_options = [
                    "Όλα"
                ]


            selected_market = st.selectbox(
                "🏪 Market",
                market_options
            )


            if (
                selected_market != "Όλα"
                and
                "market" in df_prices.columns
            ):

                df_prices = df_prices[
                    df_prices["market"]
                    ==
                    selected_market
                ]


            search_text = st.text_input(
                "🔎 Αναζήτηση",
                placeholder="Προϊόν ή barcode"
            )


            if search_text:

                search_text = (
                    search_text
                    .strip()
                    .lower()
                )


                product_search = pd.Series(
                    False,
                    index=df_prices.index
                )

                barcode_search = pd.Series(
                    False,
                    index=df_prices.index
                )


                if "product" in df_prices.columns:

                    product_search = (
                        df_prices["product"]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            search_text,
                            regex=False
                        )
                    )


                if "barcode" in df_prices.columns:

                    barcode_search = (
                        df_prices["barcode"]
                        .fillna("")
                        .astype(str)
                        .str.contains(
                            search_text,
                            regex=False
                        )
                    )


                df_prices = df_prices[
                    product_search
                    |
                    barcode_search
                ]


            st.caption(
                f"Σύνολο: {len(df_prices)} καταχωρήσεις"
            )


            for _, row in df_prices.iterrows():

                product_value = row.get(
                    "product",
                    ""
                )

                market_value = row.get(
                    "market",
                    ""
                )

                barcode_value = row.get(
                    "barcode",
                    ""
                )

                price_value = row.get(
                    "price",
                    0
                )


                if pd.isna(product_value):
                    product_value = ""

                if pd.isna(market_value):
                    market_value = ""

                if pd.isna(barcode_value):
                    barcode_value = ""


                try:
                    price_text = (
                        f"{float(price_value):.2f} €"
                    )
                except:
                    price_text = str(
                        price_value
                    )


                date_text = ""

                created_at_value = row.get(
                    "created_at"
                )


                if (
                    created_at_value is not None
                    and
                    pd.notna(created_at_value)
                ):

                    try:
                        date_text = (
                            created_at_value.strftime(
                                "%d/%m/%Y • %H:%M"
                            )
                        )
                    except:
                        date_text = str(
                            created_at_value
                        )


                st.markdown(
                    f"""
<div style="
    border:1px solid #d1d5db;
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;
    background:#ffffff;
">

    <div style="
        font-size:17px;
        font-weight:700;
        color:#111827;
        line-height:1.25;
    ">
        {product_value}
    </div>

    <div style="
        font-size:26px;
        font-weight:800;
        margin-top:6px;
        color:#111827;
    ">
        {price_text}
    </div>

    <div style="
        margin-top:5px;
        font-size:14px;
        color:#374151;
    ">
        🏪 {market_value}
    </div>

    <div style="
        font-size:12px;
        color:#6b7280;
        margin-top:5px;
    ">
        Barcode: {barcode_value}
    </div>

    <div style="
        font-size:12px;
        color:#6b7280;
        margin-top:2px;
    ">
        🕒 {date_text}
    </div>

</div>
""",
                    unsafe_allow_html=True
                )


    except Exception as e:

        st.error(
            "❌ Δεν μπόρεσα να φορτώσω τις τιμές."
        )

        st.caption(
            str(e)
        )


    st.stop()


# =========================================================
# SCANNER
# =========================================================


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


        if barcode in PRODUCTS:

            st.session_state.current_barcode = barcode


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


    if not code:

        st.session_state.manual_search_message = (
            "⚠️ Πληκτρολόγησε πρώτα ένα barcode."
        )


    elif code in PRODUCTS:

        st.session_state.current_barcode = code

        st.session_state.manual_search_message = (
            "✅ Το προϊόν βρέθηκε."
        )

        st.rerun()


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


    market = st.selectbox(
        "🏪 Market",
        MARKETS,
        index=0,
        key=(
            f"market_"
            f"{st.session_state.entry_counter}"
        )
    )


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
# ΚΑΤΑΧΩΡΗΣΕΙΣ ΤΗΣ ΤΡΕΧΟΥΣΑΣ ΣΥΝΕΔΡΙΑΣ
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
