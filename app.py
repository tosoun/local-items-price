import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from io import BytesIO
from datetime import datetime
import html
import base64

from supabase import create_client


# =========================================================
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# =========================================================
st.set_page_config(
    page_title="Καταγραφή Τιμών",
    page_icon="📱",
    layout="centered"
)


# =========================================================
# SUPABASE
# =========================================================
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

.block-container {
    padding-top: 0.2rem !important;
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

iframe {
    display: block !important;
    margin: 0 !important;
}


/* =======================================================
   STICKY MENU
======================================================= */

div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    position: -webkit-sticky !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999999 !important;
    background: #ffffff !important;
    padding-top: 8px !important;
    padding-bottom: 8px !important;
    margin-top: 0 !important;
    margin-bottom: 8px !important;
    border-bottom: 1px solid #e5e7eb !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.08) !important;
}

div[data-testid="stRadio"] {
    position: relative !important;
    background: white !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 18px !important;
}

div[data-testid="stRadio"] label {
    font-size: 17px !important;
    font-weight: 600 !important;
}


/* =======================================================
   ΚΑΡΤΕΣ ΤΙΜΩΝ
======================================================= */

.price-card {
    border: 1px solid #d8dde5;
    border-radius: 14px;
    padding: 14px 15px;
    margin-top: 4px;
    margin-bottom: 10px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.price-product {
    font-size: 17px;
    font-weight: 700;
    line-height: 1.3;
    color: #111827;
}

.price-value {
    font-size: 27px;
    font-weight: 800;
    margin-top: 7px;
    color: #111827;
}

.price-market {
    margin-top: 7px;
    font-size: 15px;
    color: #374151;
}

.price-city {
    margin-top: 4px;
    font-size: 14px;
    color: #374151;
}

.price-barcode {
    margin-top: 5px;
    font-size: 13px;
    color: #6b7280;
}

.price-date {
    margin-top: 2px;
    font-size: 13px;
    color: #6b7280;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# ΠΡΟΪΟΝΤΑ
# =========================================================
PRODUCTS = {
    "5200120690012": "ΘΕΟΝΗ – Φυσικό Μεταλλικό Νερό 0,5λ",
}


# =========================================================
# MARKETS
# =========================================================
MARKETS = [
    "Μασούτης",
    "Σκλαβενίτης",
    "ΑΒ Βασιλόπουλος",
    "My market",
    "Γαλαξίας",
    "Market In",
]


# =========================================================
# ΠΟΛΕΙΣ
# =========================================================
CITIES = [
    "— Επίλεξε πόλη —",
    "Τρίκαλα",
    "Καρδίτσα",
    "Λάρισα",
    "Βόλος",
    "Κοζάνη",
    "Πτολεμαΐδα",
    "Γρεβενά",
    "Φλώρινα",
    "Καστοριά",
    "Ιωάννινα",
    "Πρέβεζα",
    "Άρτα",
    "Κέρκυρα",
    "Κατερίνη",
]


# =========================================================
# SESSION STATE
# =========================================================
if "preview_mode" not in st.session_state:
    st.session_state.preview_mode = False

if "preview_data" not in st.session_state:
    st.session_state.preview_data = []

if "preview_return" not in st.session_state:
    st.session_state.preview_return = "📋 Τιμές"

if "main_page" not in st.session_state:
    st.session_state.main_page = "📷 Scanner"

if "prices_unlocked" not in st.session_state:
    st.session_state.prices_unlocked = False

if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False

if "delete_success" not in st.session_state:
    st.session_state.delete_success = False


# =========================================================
# ΠΡΟΕΠΙΣΚΟΠΗΣΗ EXCEL
# =========================================================
if st.session_state.preview_mode:

    st.markdown("## 📊 Προεπισκόπηση Excel")

    if st.button(
        "⬅️ Επιστροφή στην εφαρμογή",
        use_container_width=True,
        type="primary"
    ):
        st.session_state.preview_mode = False
        st.session_state.main_page = st.session_state.preview_return
        st.rerun()

    preview_df = pd.DataFrame(
        st.session_state.preview_data
    )

    if preview_df.empty:

        st.info(
            "Δεν υπάρχουν δεδομένα για προεπισκόπηση."
        )

    else:

        st.caption(
            f"Σύνολο: {len(preview_df)} καταχωρήσεις"
        )

        st.dataframe(
            preview_df,
            use_container_width=True,
            hide_index=True
        )

        preview_output = BytesIO()

        with pd.ExcelWriter(
            preview_output,
            engine="openpyxl"
        ) as writer:

            preview_df.to_excel(
                writer,
                index=False,
                sheet_name="Τιμές"
            )

            worksheet = writer.sheets["Τιμές"]

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

            for column_cells in worksheet.columns:

                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:

                    value = (
                        ""
                        if cell.value is None
                        else str(cell.value)
                    )

                    max_length = max(
                        max_length,
                        len(value)
                    )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max(max_length + 2, 10),
                    45
                )

        preview_output.seek(0)

        excel_bytes = preview_output.getvalue()

        excel_b64 = base64.b64encode(
            excel_bytes
        ).decode("utf-8")

        file_name = (
            "times_"
            + datetime.now().strftime("%d-%m-%Y_%H-%M")
            + ".xlsx"
        )

        components.html(
            f"""
            <html>
            <body style="
                margin:0;
                padding:0;
                background:white;
            ">

                <button
                    onclick="openExcel()"
                    style="
                        width:100%;
                        padding:14px;
                        font-size:16px;
                        font-weight:600;
                        border:1px solid #d1d5db;
                        border-radius:8px;
                        background:white;
                        color:#111827;
                        cursor:pointer;
                    "
                >
                    📥 Άνοιγμα Excel σε νέα καρτέλα
                </button>

                <script>

                function openExcel() {{

                    const base64 = "{excel_b64}";
                    const binary = atob(base64);
                    const bytes = new Uint8Array(binary.length);

                    for (
                        let i = 0;
                        i < binary.length;
                        i++
                    ) {{
                        bytes[i] = binary.charCodeAt(i);
                    }}

                    const blob = new Blob(
                        [bytes],
                        {{
                            type:
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        }}
                    );

                    const url = URL.createObjectURL(blob);

                    const a = document.createElement("a");

                    a.href = url;
                    a.download = "{file_name}";
                    a.target = "_blank";

                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);

                    setTimeout(
                        () => {{
                            URL.revokeObjectURL(url);
                        }},
                        5000
                    );

                }}

                </script>

            </body>
            </html>
            """,
            height=65
        )

    st.stop()


# =========================================================
# MENU
# =========================================================
page = st.radio(
    "",
    [
        "📷 Scanner",
        "📋 Τιμές"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="main_page"
)


# =========================================================
# SCANNER = ΧΩΡΙΣ ΚΩΔΙΚΟ
# =========================================================
if page == "📷 Scanner":

    st.session_state.prices_unlocked = False
    st.session_state.confirm_delete_all = False


# =========================================================
# ΣΕΛΙΔΑ ΤΙΜΩΝ
# =========================================================
if page == "📋 Τιμές":

    # =====================================================
    # ΚΩΔΙΚΟΣ ΠΡΟΣΒΑΣΗΣ
    # =====================================================
    if not st.session_state.prices_unlocked:

        st.markdown(
            "## 🔒 Πρόσβαση στις Τιμές"
        )

        access_code = st.text_input(
            "🔑 Κωδικός πρόσβασης",
            type="password",
            key="prices_access_code"
        )

        if st.button(
            "🔓 Είσοδος",
            type="primary",
            use_container_width=True,
            key="prices_login_button"
        ):

            if access_code == "2845":

                st.session_state.prices_unlocked = True
                st.rerun()

            else:

                st.error(
                    "❌ Λάθος κωδικός."
                )

        st.stop()


    # =====================================================
    # ΤΙΜΕΣ
    # =====================================================
    st.markdown(
        "## 📋 Καταχωρημένες Τιμές"
    )


    # =====================================================
    # ΜΗΝΥΜΑ ΕΠΙΤΥΧΗΜΕΝΗΣ ΔΙΑΓΡΑΦΗΣ
    # =====================================================
    if st.session_state.delete_success:

        st.success(
            "✅ Όλες οι καταχωρήσεις διαγράφηκαν από τη βάση."
        )

        st.session_state.delete_success = False


    # =====================================================
    # ΑΝΑΝΕΩΣΗ
    # =====================================================
    if st.button(
        "🔄 Ανανέωση",
        use_container_width=True
    ):
        st.rerun()


    # =====================================================
    # DEL
    # =====================================================
    if st.button(
        "🗑️ DEL – Διαγραφή λίστας",
        use_container_width=True,
        key="delete_all_button"
    ):

        st.session_state.confirm_delete_all = True


    # =====================================================
    # ΕΠΙΒΕΒΑΙΩΣΗ DEL
    # =====================================================
    if st.session_state.confirm_delete_all:

        st.warning(
            "⚠️ ΠΡΟΣΟΧΗ: Θα διαγραφούν ΟΛΕΣ οι καταχωρήσεις από το Supabase."
        )

        col_cancel, col_delete = st.columns(2)

        with col_cancel:

            if st.button(
                "❌ Ακύρωση",
                use_container_width=True,
                key="cancel_delete_all"
            ):

                st.session_state.confirm_delete_all = False
                st.rerun()


        with col_delete:

            if st.button(
                "🗑️ Οριστική διαγραφή",
                type="primary",
                use_container_width=True,
                key="confirm_delete_all_button"
            ):

                try:

                    # =========================================
                    # ΠΡΑΓΜΑΤΙΚΗ ΔΙΑΓΡΑΦΗ ΑΠΟ SUPABASE
                    # =========================================
                    supabase.table(
                        "price_records"
                    ).delete().neq(
                        "id",
                        -1
                    ).execute()


                    # =========================================
                    # ΕΛΕΓΧΟΣ ΜΕΤΑ ΤΗ ΔΙΑΓΡΑΦΗ
                    # =========================================
                    check_response = (
                        supabase
                        .table("price_records")
                        .select("id")
                        .execute()
                    )

                    remaining_rows = (
                        check_response.data
                        if check_response.data
                        else []
                    )


                    # =========================================
                    # ΑΝ ΟΝΤΩΣ ΕΓΙΝΑΝ 0
                    # =========================================
                    if len(remaining_rows) == 0:

                        st.session_state.confirm_delete_all = False

                        # Καθαρίζουμε και την τοπική λίστα
                        if "records" in st.session_state:
                            st.session_state.records = []

                        st.session_state.delete_success = True

                        st.rerun()


                    # =========================================
                    # ΑΝ ΥΠΑΡΧΟΥΝ ΑΚΟΜΑ ΕΓΓΡΑΦΕΣ
                    # =========================================
                    else:

                        st.error(
                            "❌ Η διαγραφή δεν ολοκληρώθηκε στη βάση."
                        )

                        st.warning(
                            f"Παραμένουν {len(remaining_rows)} καταχωρήσεις."
                        )


                except Exception as e:

                    st.error(
                        "❌ Σφάλμα κατά τη διαγραφή από το Supabase."
                    )

                    st.caption(
                        str(e)
                    )


    # =====================================================
    # ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ
    # =====================================================
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


        # =================================================
        # ΚΕΝΗ ΒΑΣΗ
        # =================================================
        if not rows:

            st.info(
                "Δεν υπάρχουν ακόμη καταχωρήσεις."
            )


        else:

            df_prices = pd.DataFrame(rows)


            # =================================================
            # ΗΜΕΡΟΜΗΝΙΑ / ΩΡΑ
            # =================================================
            if "created_at" in df_prices.columns:

                df_prices["created_at"] = pd.to_datetime(
                    df_prices["created_at"],
                    utc=True,
                    errors="coerce"
                )

                df_prices["created_at"] = (
                    df_prices["created_at"]
                    .dt.tz_convert("Europe/Athens")
                )


            # =================================================
            # MARKET FILTER
            # =================================================
            if "market" in df_prices.columns:

                market_options = (
                    ["Όλα"]
                    +
                    sorted(
                        df_prices["market"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                )

            else:

                market_options = ["Όλα"]


            selected_market = st.selectbox(
                "🏪 Market",
                market_options,
                key="filter_market"
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


            # =================================================
            # CITY FILTER
            # =================================================
            if "city" in df_prices.columns:

                valid_cities = (
                    df_prices["city"]
                    .dropna()
                    .astype(str)
                )

                valid_cities = valid_cities[
                    valid_cities.str.strip() != ""
                ]

                city_options = (
                    ["Όλες"]
                    +
                    sorted(
                        valid_cities
                        .unique()
                        .tolist()
                    )
                )

            else:

                city_options = ["Όλες"]


            selected_city = st.selectbox(
                "🏙️ Πόλη",
                city_options,
                key="filter_city"
            )


            if (
                selected_city != "Όλες"
                and
                "city" in df_prices.columns
            ):

                df_prices = df_prices[
                    df_prices["city"]
                    ==
                    selected_city
                ]


            # =================================================
            # SEARCH
            # =================================================
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
                    product_search |
                    barcode_search
                ]


            st.caption(
                f"Σύνολο: {len(df_prices)} καταχωρήσεις"
            )


            # =================================================
            # EXPORT DATAFRAME
            # =================================================
            export_df = pd.DataFrame()


            if "created_at" in df_prices.columns:

                export_df["Ημερομηνία"] = (
                    df_prices["created_at"]
                    .dt.strftime("%d/%m/%Y")
                )

                export_df["Ώρα"] = (
                    df_prices["created_at"]
                    .dt.strftime("%H:%M")
                )

            else:

                export_df["Ημερομηνία"] = ""
                export_df["Ώρα"] = ""


            if "market" in df_prices.columns:

                export_df["Market"] = (
                    df_prices["market"]
                    .fillna("")
                )

            else:

                export_df["Market"] = ""


            if "city" in df_prices.columns:

                export_df["Πόλη"] = (
                    df_prices["city"]
                    .fillna("")
                )

            else:

                export_df["Πόλη"] = ""


            if "barcode" in df_prices.columns:

                export_df["Barcode"] = (
                    df_prices["barcode"]
                    .fillna("")
                    .astype(str)
                )

            else:

                export_df["Barcode"] = ""


            if "product" in df_prices.columns:

                export_df["Προϊόν"] = (
                    df_prices["product"]
                    .fillna("")
                )

            else:

                export_df["Προϊόν"] = ""


            if "price" in df_prices.columns:

                export_df["Τιμή (€)"] = pd.to_numeric(
                    df_prices["price"],
                    errors="coerce"
                )

            else:

                export_df["Τιμή (€)"] = ""


            # =================================================
            # EXCEL PREVIEW
            # =================================================
            if st.button(
                "📊 Προεπισκόπηση Excel",
                use_container_width=True
            ):

                st.session_state.preview_data = (
                    export_df.to_dict(
                        orient="records"
                    )
                )

                st.session_state.preview_return = (
                    "📋 Τιμές"
                )

                st.session_state.preview_mode = True

                st.rerun()


            # =================================================
            # ΚΑΡΤΕΣ
            # =================================================
            for _, row in df_prices.iterrows():

                product_value = row.get(
                    "product",
                    ""
                )

                market_value = row.get(
                    "market",
                    ""
                )

                city_value = row.get(
                    "city",
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

                if pd.isna(city_value):
                    city_value = ""

                if pd.isna(barcode_value):
                    barcode_value = ""


                product_value = html.escape(
                    str(product_value)
                )

                market_value = html.escape(
                    str(market_value)
                )

                city_value = html.escape(
                    str(city_value)
                )

                barcode_value = html.escape(
                    str(barcode_value)
                )


                try:

                    price_text = (
                        f"{float(price_value):.2f} €"
                    )

                except Exception:

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

                    except Exception:

                        date_text = str(
                            created_at_value
                        )


                city_html = ""

                if city_value:

                    city_html = (
                        f'<div class="price-city">'
                        f'🏙️ {city_value}'
                        f'</div>'
                    )


                card_html = (
                    '<div class="price-card">'
                    f'<div class="price-product">{product_value}</div>'
                    f'<div class="price-value">{price_text}</div>'
                    f'<div class="price-market">🏪 {market_value}</div>'
                    f'{city_html}'
                    f'<div class="price-barcode">Barcode: {barcode_value}</div>'
                    f'<div class="price-date">🕒 {date_text}</div>'
                    '</div>'
                )


                st.markdown(
                    card_html,
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
# SCANNER COMPONENT
# =========================================================
barcode_scanner = components.declare_component(
    "barcode_scanner",
    path="scanner_component"
)


# =========================================================
# SESSION STATE SCANNER
# =========================================================
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


# =========================================================
# ΜΗΝΥΜΑ ΕΠΙΤΥΧΙΑΣ
# =========================================================
if st.session_state.saved_message:

    st.success(
        "✅ Η τιμή αποθηκεύτηκε!"
    )

    st.session_state.saved_message = False


# =========================================================
# SCANNER
# =========================================================
barcode_result = barcode_scanner(
    reset_token=st.session_state.reset_token,
    scanner_message=st.session_state.scanner_message,
    key="barcode_scanner_main",
    default=None
)

st.session_state.scanner_message = ""


# =========================================================
# ΑΠΟΤΕΛΕΣΜΑ SCANNER
# =========================================================
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

            st.session_state.current_barcode = (
                barcode
            )


        else:

            st.session_state.current_barcode = None

            st.session_state.scanner_message = (
                "⛔ Ο κωδικός δεν υπάρχει"
            )

            st.session_state.reset_token += 1

            st.rerun()


# =========================================================
# ΧΕΙΡΟΚΙΝΗΤΗ ΑΝΑΖΗΤΗΣΗ
# =========================================================
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


# =========================================================
# ΜΗΝΥΜΑ ΧΕΙΡΟΚΙΝΗΤΗΣ ΑΝΑΖΗΤΗΣΗΣ
# =========================================================
if st.session_state.manual_search_message:

    message = (
        st.session_state.manual_search_message
    )


    if message.startswith("✅"):

        st.success(message)


    elif message.startswith("⛔"):

        st.warning(message)


    else:

        st.info(message)


    st.session_state.manual_search_message = ""


# =========================================================
# ΠΡΟΪΟΝ / MARKET / ΠΟΛΗ / ΤΙΜΗ
# =========================================================
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


    # =====================================================
    # MARKET
    # =====================================================
    market = st.selectbox(
        "🏪 Market",
        MARKETS,
        index=0,
        key=(
            f"market_"
            f"{st.session_state.entry_counter}"
        )
    )


    # =====================================================
    # ΠΟΛΗ
    # =====================================================
    city = st.selectbox(
        "🏙️ Πόλη *",
        CITIES,
        index=0,
        key=(
            f"city_"
            f"{st.session_state.entry_counter}"
        )
    )


    # =====================================================
    # ΤΙΜΗ
    # =====================================================
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


    # =====================================================
    # ΑΠΟΘΗΚΕΥΣΗ
    # =====================================================
    if st.button(
        "💾 Αποθήκευση τιμής",
        type="primary",
        use_container_width=True
    ):


        if city == "— Επίλεξε πόλη —":

            st.warning(
                "⚠️ Επίλεξε πρώτα πόλη."
            )


        elif price <= 0:

            st.warning(
                "⚠️ Γράψε πρώτα την τιμή."
            )


        else:

            now = datetime.now()


            try:

                # =========================================
                # SUPABASE
                # =========================================
                supabase.table(
                    "price_records"
                ).insert(
                    {
                        "market": market,
                        "city": city,
                        "barcode": barcode,
                        "product": product,
                        "price": float(price),
                    }
                ).execute()


                # =========================================
                # ΤΟΠΙΚΕΣ ΚΑΤΑΧΩΡΗΣΕΙΣ
                # =========================================
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

                        "Πόλη":
                            city,

                        "Barcode":
                            barcode,

                        "Προϊόν":
                            product,

                        "Τιμή (€)":
                            float(price),
                    }
                )


                # =========================================
                # RESET
                # =========================================
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


# =========================================================
# ΚΑΤΑΧΩΡΗΣΕΙΣ ΤΡΕΧΟΥΣΑΣ ΣΥΝΕΔΡΙΑΣ
# =========================================================
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


    if st.button(
        "📊 Προεπισκόπηση Excel",
        use_container_width=True,
        key="scanner_excel_preview"
    ):

        st.session_state.preview_data = (
            df.to_dict(
                orient="records"
            )
        )

        st.session_state.preview_return = (
            "📷 Scanner"
        )

        st.session_state.preview_mode = True

        st.rerun()
