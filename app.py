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
   ΚΡΥΨΙΜΟ STREAMLIT TOOLBAR
======================================================= */

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stStatusWidget"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}


/* =======================================================
   TOP MENU
======================================================= */

div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    position: -webkit-sticky !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999999 !important;

    background: transparent !important;

    padding-top: 8px !important;
    padding-bottom: 8px !important;

    margin-top: 0 !important;
    margin-bottom: 8px !important;

    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stRadio"] {
    position: relative !important;
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 20px !important;
    background: transparent !important;
}

div[data-testid="stRadio"] label {
    font-size: 17px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 4px 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}


/* =======================================================
   ΚΑΡΤΕΣ DATABASE
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
    '5200120690012': 'ΘΕΟΝΗ – Φυσικό Μεταλλικό Νερό 0,5λ',
    '5203190210043': 'ΤΡΙΚΚΗ – Φρέσκο Γάλα Πλήρες 1λ',
    '5203190210012': 'ΤΡΙΚΚΗ – Φρέσκο Γάλα Ελαφρύ 1λ',
    '5204139001012': 'ΓΑΛΑ ΦΡΕΣΚΟ ΕΒΟΛ ΠΛΗΡΕΣ 1Λ',
    '5204139001036': 'ΓΑΛΑ  ΦΡΕΣΚΟ ΕΒΟΛ ΕΛΑΦΡΥ',
    '5204139001074': 'ΓΑΛΑ ΚΑΚΑΟ ΕΒΟΛ 230ΜL',
    '5204139001050': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΕΒΟΛ 6,7% 290ΓΡ',
    '5204139001531': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΕΒΟΛ 2% 250ΓΡ',
    '5204139001784': 'ΓΑΛΑ ΤΟ ΔΙΚΟ ΜΑΣ ΣΥΝΕΤΕΡΙΣΤΙΚΟ 1Λ',
    '5204139001777': 'ΓΑΛΑ ΤΟ ΔΙΚΟ ΜΑΣ ΣΥΝΕΤΕΡΙΣΤΙΚΟ',
    '2102280000000': 'ΣΚΛΗΡΟ ΤΥΡΙ ΟΛΥΜΠΟΣ ΧΥΜΑ ΚΕΦΑΛΙ',
    '2102281000000': 'ΒΟΥΤΥΡΟ ΑΓΕΛΑΔΟΣ ΟΛΥΜΠΟΣ ΧΥΜΑ',
    '5202178001116': 'ΓΑΛΑ ΟΛΥΜΠΟΣ ΕΠΙΛΕΓΜΕΝΟ 3,7%',
    '5202178001178': 'ΓΑΛΑ ΟΛΥΜΠΟΣ ΕΠΙΛΕΓΜΕΝΟ 1,7%',
    '5202178050084': 'ΓΑΛΑ ΟΛΥΜΠΟΣ ΕΠΙΛΕΓΜΕΝΟ 1,7%Λ 1,5ΛΙΤ',
    '5202178050077': 'ΓΑΛΑ ΟΛΥΜΠΟΣ ΕΠΙΛΕΓΜΕΝΟ 3,7%Λ 1,5ΛΙΤ',
    '5202178082795': 'ΚΕΦΙΡ 1%ΛΙΠ ΟΛΥΜΠΟΣ 2Χ150ΓΡ',
    '5202178000010': 'ΓΑΛΑ ΛΕΥΚΟ ΟΛΥΜΠΟΣ 3,5% 1ΛΙΤ',
    '5202178000034': 'ΓΑΛΑ ΛΕΥΚΟ ΟΛΥΜΠΟΣ 1,5% 1ΛΙΤ',
    '5200112010231': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓ ΦΑΡΜΑ ΝΟΤΑΣ 2%Λ 2Χ200ΓΡ',
    '5200112010217': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓ ΦΑΡΜΑ ΝΟΤΑΣ 10%Λ 2Χ200ΓΡ',
    '5200112010248': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓ ΦΑΡΜΑ ΝΟΤΑΣ 10%Λ 1ΚΙΛΟΥ',
    '5200112010446': 'ΓΙΑΟΥΡΤ ΠΡΟΒΕΙΟ ΦΑΡΜΑ ΝΟΤΑΣ ΠΑΡΑΔ 280ΓΡ',
    '5200112010422': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓ ΦΑΡΜΑ ΝΟΤΑΣ 2%Λ 1ΚΙΛΟΥ',
    '5200112011474': 'ΓΙΑΟΥΡΤΙ ΑΓΕΛΑΔ ΦΑΡΜΑ ΝΟΤΑΣ ΠΑΡΑΔ 280ΓΡ',
    '5200112010484': 'ΕΠΙΔ ΚΡΕΜΑ ΒΑΝΙΛΙΑ ΦΑΡΜΑ ΝΟΤΑΣ 180ΓΡ',
    '5200148780016': 'ΓΑΛΑ ΦΡΕΣΚΟ ΑΓΕΛΑΔ ΠΛΗΡΕΣ ΘΕΣΓΑΛΑ 1Λ PET',
    '5200148780023': 'ΓΑΛΑ ΦΡΕΣΚΟ ΑΓΕΛΑΔ ΕΛΑΦΡΥ ΘΕΣΓΑΛΑ 1Λ PET',
    '5200148780047': 'ΡΥΖΟΓΑΛΟ ΠΑΡΑΔΟΣΙΑΚΟ ΘΕΣΓΑΛΑ 180ΓΡ',
    '5200148780030': 'ΚΡΕΜΑ ΒΑΝΙΛΙΑ ΠΑΡΑΔΟΣΙΑΚΗ ΘΕΣΓΑΛΑ 180ΓΡ',
    '5200148780054': 'ΚΡΕΜΑ ΚΑΚΑΟ ΘΕΣΓΑΛΑ 180ΓΡ',
    '5200148780351': 'ΓΑΛΑ ΚΑΚΑΟ ΘΕΣΓΑΛΑ 330ML',
    '5200148780368': 'ΚΕΦΙΡ ΚΛΑΣΙΚΟ ΧΩΡ ΓΛΟΥΤΕΝΗ ΘΕΣΓΑΛΑ 330ML',
    '5200148780375': 'ΚΕΦΙΡ ΦΡΑΟΥΛΑ ΘΕΣΓΑΛΑ 330ML',
    '5200148780382': 'ΚΕΦΙΡ ΡΟΔΙ ΘΕΣΓΑΛΑ 330ML',
    '5200106910851': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒ. ΧΑΤΖΗΣ 200ΓΡ',
    '5200106910837': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΧΑΤΖΗΣ 280ΓΡ',
    '5200106910844': 'ΓΙΑΟΡΤΙ ΠΡΟΒΕΙΟ ΑΠΑΧΟ 1% ΧΑΤΖΗ',
    '5200106910509': 'ΚΡΕΜΑ ΒΑΝΙΛΙΑ ΧΑΤΖΗΣ 200ΓΡ',
    '5200106910608': 'ΚΡΕΜΑ ΣΟΚΟΛΑΤΑ ΧΑΤΖΗΣ 200ΓΡ',
    '5200106910707': 'ΡΥΖΟΓΑΛΟ ΧΑΤΖΗΣ 200ΓΡ',
    '5203190210029': 'ΓΑΛΑ ΛΕΥΚΟ ΤΡΙΚΚΗ 3,5% 1/2ΛΙΤ',
    '5203190210050': 'ΓΑΛΑ ΚΑΚΑΟ ΤΡΙΚΚΗ 1/2Λ',
    '5203190210081': 'ΞΙΝΟΓΑΛΟ ΤΡΙΚΚΗ 1/2ΛΙΤ',
    '5203190210104': 'ΓΙΑΟΥΡΤΙ ΑΓΕΛ ΤΡΙΚΚΗ 200-220ΓΡ',
    '5203190210111': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΤΡΙΚΚΗ 304-320ΓΡ',
    '5203190210173': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΤΡΙΚΚΗ 450ΓΡ ΠΗΛΙΝΟ',
    '5203190210036': 'ΓΑΛΑ ΛΕΥΚΟ ΤΡΙΚΚΗ ΕΛΑΦΡΥ 1% 1/2ΛΙΤ',
    '5203190210123': 'ΓΙΑΟΥΡΤΙ ΠΡΟΒΕΙΟ ΤΡΙΚΚΗ ΠΑΡΑΔ 200-220ΓΡ',
    '5203190210548': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓ ΤΡΙΚΚΗ 10% 1Κ',
    '5203190212269': 'ΓΙΑΟΥΡΤΙ ΑΓΕΛΑΔΟΣ ΤΡΙΚΚΗ 2Χ200ΓΡ ET',
    '5203190212245': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓΙΣΤΟ 2% ΤΡΙΚΚΗ 2Χ200ΓΡ',
    '5203190212221': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓΙΣΤΟ 10% ΤΡΙΚΚΗ 2Χ200ΓΡ',
    '5203190215031': 'ΕΠΙΔ ΑΛΑ ΚΡΕΜ ΤΡΙΚΚΗ 180-190ΓΡ',
    '5203190215017': 'ΡΥΖΟΓΑΛΟ ΤΡΙΚΚΗ 170ΓΡ',
    '5203190210517': 'ΓΙΑΟΥΡΤΙ ΣΤΡΑΓΓΙΣΤΟ ΤΡΙΚΚΗ 2%Λ 1ΚΙΛΟΥ',
    '5203190203069': 'ΕΠΙΔΟΡΠΙΟ ΜΕ ΓΑΛΑ & ΚΑΚΑΟ 180ΓΡ ΤΡΙΚΚΗ',
    '5206501001019': 'ΑΡΤΟΣΚΕΥΑΣ ΣΙΜΙΓΔΑΛΙ 350ΓΡ ΑΡΤΟΓΕΥΣΕΙΣ',
    '5206501001026': 'ΑΡΤΟΣΚΕΥΑΣ ΛΕΥΚΟ 350ΓΡ ΑΡΤΟΓΕΥΣΕΙΣ',
    '5206501001095': 'ΑΡΤΟΣΚΕΥΑΣ ΜΠΑΓΚΕΤΑ ΣΙΜΙΓΔΑΛΙ 350ΓΡ ΑΡΤΟ',
    '5206501001033': 'ΑΡΤΟΣΚΕΥΑΣΜΑ ΖΥΜΩΤΟ 750ΓΡ ΑΡΤΟΓΕΥΣΕΙΣ',
    '5206501001057': 'ΑΡΤΟΣΚΕΥΑΣ ΖΥΜΩΤΟ ΟΛΙΚΗΣ ΑΛΕΣΗΣ 750ΓΡ ΑΡ',
    '2107010000000': 'ΑΡΤΟΣΚ ΚΟΥΛΟΥΡΑ ΧΩΡΙΑΤΙΚΗ 350ΓΡ ΑΡΤΟΓΕΥΣ',
    '5206501001262': 'ΑΡΤΟΣΚ ΖΥΜΩΤΟ ΨΩΜΙ ΞΥΝ 600ΓΡ ΑΡΤΟΓΕΥΣΕΙΣ',
}


# Προϊόντα της λίστας χωρίς barcode: εσωτερικά αναγνωριστικά μόνο
# για τη χειροκίνητη αναζήτηση (δεν αποθηκεύονται ως barcode).
PRODUCTS.update({
    "NO_BARCODE_1": "ΦΕΤΑ ΧΩΤΟΣ ΧΥΜΑ ΔΟΧΕΙΟ",
    "NO_BARCODE_2": "ΦΕΤΑ ΑΒΡΑΜΟΥΛΗ ΧΥΜΑ",
    "NO_BARCODE_3": "ΦΕΤΑ ΕΛΑΣΣΟΝΑΣ ΕΞΑΡΧΟΣ",
})
NO_BARCODE_IDS = {"NO_BARCODE_1", "NO_BARCODE_2", "NO_BARCODE_3"}


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
    st.session_state.preview_return = "🗄️ Database"

if "main_page" not in st.session_state:
    st.session_state.main_page = "📷 Scanner"

if "prices_unlocked" not in st.session_state:
    st.session_state.prices_unlocked = False

if "confirm_delete_all" not in st.session_state:
    st.session_state.confirm_delete_all = False

if "delete_success" not in st.session_state:
    st.session_state.delete_success = False


# =========================================================
# ΠΡΟΕΠΙΣΚΟΠΗΣΗ
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
        "🗄️ Database"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="main_page"
)


# =========================================================
# RESET DATABASE LOCK
# =========================================================
if page == "📷 Scanner":

    st.session_state.prices_unlocked = False
    st.session_state.confirm_delete_all = False


# =========================================================
# DATABASE
# =========================================================
if page == "🗄️ Database":

    # =====================================================
    # LOGIN
    # =====================================================
    if not st.session_state.prices_unlocked:

        st.markdown(
            """
            <div style="
                font-size:22px;
                font-weight:700;
                margin-top:8px;
                margin-bottom:6px;
                line-height:1.2;
                color:#111827;
            ">
                🔒 Πρόσβαση στη Database
            </div>
            """,
            unsafe_allow_html=True
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
    # DATABASE TITLE
    # =====================================================
    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            margin-top:8px;
            margin-bottom:6px;
            line-height:1.2;
            color:#111827;
        ">
            📋 Καταχωρημένες Τιμές
        </div>
        """,
        unsafe_allow_html=True
    )


    if st.session_state.delete_success:

        st.success(
            "✅ Όλες οι καταχωρήσεις διαγράφηκαν από τη βάση."
        )

        st.session_state.delete_success = False


    # =====================================================
    # REFRESH
    # =====================================================
    if st.button(
        "🔄 Ανανέωση",
        use_container_width=True,
        key="database_refresh"
    ):

        st.rerun()


    # =====================================================
    # DELETE
    # =====================================================
    if st.button(
        "🗑️ DEL – Διαγραφή λίστας",
        use_container_width=True,
        key="delete_all_button"
    ):

        st.session_state.confirm_delete_all = True


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

                    supabase.table(
                        "price_records"
                    ).delete().neq(
                        "id",
                        -1
                    ).execute()

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

                    if len(remaining_rows) == 0:

                        st.session_state.confirm_delete_all = False

                        if "records" in st.session_state:
                            st.session_state.records = []

                        st.session_state.delete_success = True

                        st.rerun()

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
    # DATA
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


        if not rows:

            st.info(
                "Δεν υπάρχουν ακόμη καταχωρήσεις."
            )


        else:

            df_prices = pd.DataFrame(rows)


            # =================================================
            # CREATED AT
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
                placeholder="Προϊόν ή barcode",
                key="database_search"
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
            # PREVIEW
            # =================================================
            if st.button(
                "📊 Προεπισκόπηση",
                use_container_width=True,
                key="database_excel_preview"
            ):

                st.session_state.preview_data = (
                    export_df.to_dict(
                        orient="records"
                    )
                )

                st.session_state.preview_return = (
                    "🗄️ Database"
                )

                st.session_state.preview_mode = True

                st.rerun()


            # =================================================
            # CARDS
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
# SCANNER SESSION STATE
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
# SAVE MESSAGE
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


# =========================================================
# COPYRIGHT
# =========================================================
st.markdown(
    """
    <div style="
        width:100%;
        text-align:right;
        font-size:11px;
        font-weight:400;
        color:#8a8f98;
        margin-top:-4px;
        margin-bottom:6px;
        padding-right:4px;
        line-height:1.2;
        letter-spacing:0.1px;
    ">
        © 2026 tosounidis — All rights reserved
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# RESET SCANNER MESSAGE
# =========================================================
st.session_state.scanner_message = ""


# =========================================================
# BARCODE RESULT
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
# MANUAL SEARCH TITLE
# =========================================================
st.markdown(
    """
    <div style="
        font-size:22px;
        font-weight:700;
        margin-top:8px;
        margin-bottom:6px;
        line-height:1.2;
        color:#111827;
    ">
        🔎 Χειροκίνητη αναζήτηση
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MANUAL SEARCH BY BARCODE OR DESCRIPTION
# =========================================================
manual_query = st.text_input(
    "Barcode ή περιγραφή προϊόντος",
    placeholder="Πληκτρολόγησε barcode ή μέρος της περιγραφής",
    key="manual_barcode_input"
)

if "manual_matches" not in st.session_state:
    st.session_state.manual_matches = []

if st.button(
    "🔎 Αναζήτηση προϊόντος",
    use_container_width=True,
    key="manual_search_button"
):
    query = manual_query.strip()
    st.session_state.manual_matches = []
    st.session_state.current_barcode = None

    if not query:
        st.session_state.manual_search_message = (
            "⚠️ Πληκτρολόγησε barcode ή περιγραφή προϊόντος."
        )
    elif query in PRODUCTS:
        st.session_state.current_barcode = query
        st.session_state.manual_search_message = "✅ Το προϊόν βρέθηκε."
    else:
        # Αναζήτηση χωρίς διάκριση πεζών/κεφαλαίων και τόνων.
        import unicodedata

        def normalize_search(value):
            value = unicodedata.normalize("NFD", str(value).casefold())
            return "".join(
                char for char in value
                if unicodedata.category(char) != "Mn"
            )

        normalized_query = normalize_search(query)
        matches = [
            code for code, description in PRODUCTS.items()
            if normalized_query in normalize_search(description)
            or query in code
        ]
        if len(matches) == 1:
            st.session_state.current_barcode = matches[0]
            st.session_state.manual_search_message = "✅ Το προϊόν βρέθηκε."
        elif matches:
            st.session_state.manual_matches = matches
            st.session_state.manual_search_message = (
                f"🔎 Βρέθηκαν {len(matches)} προϊόντα. Επίλεξε το σωστό."
            )
        else:
            st.session_state.manual_search_message = (
                "⛔ Δεν βρέθηκε προϊόν με αυτό το barcode ή την περιγραφή."
            )
    st.rerun()

if st.session_state.manual_matches:
    selected_code = st.selectbox(
        "Επίλεξε προϊόν",
        st.session_state.manual_matches,
        format_func=lambda code: (
            PRODUCTS[code] if code in NO_BARCODE_IDS
            else f"{PRODUCTS[code]} — {code}"
        ),
        key="manual_selected_product"
    )
    if st.button(
        "✅ Επιλογή προϊόντος",
        use_container_width=True,
        key="manual_select_button"
    ):
        st.session_state.current_barcode = selected_code
        st.session_state.manual_matches = []
        st.session_state.manual_search_message = "✅ Το προϊόν επιλέχθηκε."
        st.rerun()


# =========================================================
# MANUAL SEARCH MESSAGE
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
# PRODUCT FORM
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


    if barcode in NO_BARCODE_IDS:
        st.caption("Χωρίς barcode — χειροκίνητη καταχώρηση")
    else:
        st.caption(f"Barcode: {barcode}")


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
    # CITY
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
    # PRICE — ΜΕΓΑΛΟ ΑΡΙΘΜΗΤΙΚΟ ΠΛΗΚΤΡΟΛΟΓΙΟ (iOS / ANDROID)
    # =====================================================
    price_key = f"keypad_price_{st.session_state.entry_counter}_{barcode}"
    if price_key not in st.session_state:
        st.session_state[price_key] = ""

    @st.dialog("💶 Καταχώρηση τιμής", width="small")
    def price_keypad():
        # Τετράγωνο αριθμητικό πληκτρολόγιο, διάταξη τηλεφώνου.
        st.markdown("""
        <style>
        div[role="dialog"] {
            width: min(96vw, 390px) !important;
            max-width: 390px !important;
        }
        div[role="dialog"] div[data-testid="stButton"] button {
            min-height: 78px !important;
            height: 78px !important;
            padding: 0 !important;
            border-radius: 12px !important;
            font-size: 32px !important;
            font-weight: 750 !important;
            touch-action: manipulation;
        }
        div[role="dialog"] div[data-testid="stHorizontalBlock"] {
            gap: 8px !important;
        }
        /* Μικρότερα πλήκτρα ενεργειών κάτω από το αριθμητικό τετράγωνο. */
        div[role="dialog"] div[data-testid="stHorizontalBlock"]:last-of-type
        div[data-testid="stButton"] button {
            font-size: 16px !important;
            min-height: 52px !important;
            height: 52px !important;
        }
        @media (max-width: 420px) {
            div[role="dialog"] div[data-testid="stButton"] button {
                min-height: 72px !important;
                height: 72px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        value = st.session_state[price_key]
        st.markdown(
            f"<div style='text-align:center;font-size:38px;font-weight:800;"
            f"padding:12px 0'>{html.escape(value or '0')} €</div>",
            unsafe_allow_html=True,
        )

        for row_index, keys in enumerate((("1", "2", "3"), ("4", "5", "6"),
                                          ("7", "8", "9"), (",", "0", "⌫"))):
            cols = st.columns(3, gap="small")
            for col, digit in zip(cols, keys):
                with col:
                    if st.button(digit, key=f"pad_{row_index}_{digit}", use_container_width=True):
                        current = st.session_state[price_key]
                        if digit == "⌫":
                            current = current[:-1]
                        elif digit == ",":
                            if "," not in current:
                                current = (current or "0") + ","
                        elif len(current.replace(",", "")) < 9:
                            if "," in current:
                                cents = current.split(",", 1)[1]
                                if len(cents) < 2:
                                    current += digit
                            else:
                                current = digit if current == "0" else current + digit
                        st.session_state[price_key] = current
                        st.rerun(scope="fragment")

        col_clear, col_cancel, col_ok = st.columns(3, gap="small")
        with col_clear:
            if st.button("C", use_container_width=True, key="pad_clear"):
                st.session_state[price_key] = ""
                st.rerun(scope="fragment")
        with col_cancel:
            if st.button("Άκυρο", use_container_width=True, key="pad_cancel"):
                st.session_state[price_key] = ""
                st.rerun()
        with col_ok:
            if st.button("ΟΚ ✓", type="primary", use_container_width=True, key="pad_ok"):
                st.rerun()

    st.markdown("**💶 Τιμή (€)**")
    displayed_price = st.session_state[price_key]
    if st.button(
        f"{displayed_price or 'Πατήστε για εισαγωγή τιμής'} €",
        key=f"open_price_keypad_{st.session_state.entry_counter}_{barcode}",
        use_container_width=True,
    ):
        price_keypad()

    price = float(displayed_price.replace(",", ".")) if displayed_price and displayed_price != "," else 0.0


    # =====================================================
    # SAVE
    # =====================================================
    if st.button(
        "💾 Αποθήκευση τιμής",
        type="primary",
        use_container_width=True,
        key="save_price_button"
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

                supabase.table(
                    "price_records"
                ).insert(
                    {
                        "market": market,
                        "city": city,
                        "barcode": "" if barcode in NO_BARCODE_IDS else barcode,
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

                        "Πόλη":
                            city,

                        "Barcode":
                            "" if barcode in NO_BARCODE_IDS else barcode,

                        "Προϊόν":
                            product,

                        "Τιμή (€)":
                            float(price),
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


# =========================================================
# CURRENT SESSION RECORDS
# =========================================================
if st.session_state.records:

    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            margin-top:8px;
            margin-bottom:6px;
            line-height:1.2;
            color:#111827;
        ">
            📋 Καταχωρήσεις
        </div>
        """,
        unsafe_allow_html=True
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
        "📊 Προεπισκόπηση",
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
