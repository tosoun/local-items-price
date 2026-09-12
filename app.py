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
   ΚΡΥΨΙΜΟ STREAMLIT TOOLBAR / FORK / GITHUB / MENU
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
   TOP MENU - ΟΧΙ STICKY, ΑΛΛΑ CLICKABLE
======================================================= */

div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    position: relative !important;
    top: auto !important;
    z-index: 1000 !important;

    background: transparent !important;

    padding-top: 8px !important;
    padding-bottom: 8px !important;

    margin-top: 0 !important;
    margin-bottom: 8px !important;

    border: none !important;
    box-shadow: none !important;

    pointer-events: auto !important;
}

div[data-testid="stRadio"] {
    position: relative !important;
    z-index: 1001 !important;

    background: transparent !important;

    margin: 0 !important;
    padding: 0 !important;

    border: none !important;
    box-shadow: none !important;

    pointer-events: auto !important;
}

div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 20px !important;

    background: transparent !important;

    pointer-events: auto !important;
}

div[data-testid="stRadio"] label {
    position: relative !important;
    z-index: 1002 !important;

    font-size: 17px !important;
    font-weight: 600 !important;

    margin: 0 !important;
    padding: 4px 0 !important;

    background: transparent !important;

    border: none !important;
    box-shadow: none !important;

    cursor: pointer !important;
    pointer-events: auto !important;
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
                        bytes[i] =
                            binary.charCodeAt(i);
                    }}

                    const blob = new Blob(
                        [bytes],
                        {{
                            type:
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        }}
                    );

                    const url =
                        URL.createObjectURL(blob);

                    const a =
                        document.createElement("a");

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
