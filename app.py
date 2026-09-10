import streamlit as st
import pandas as pd
import zxingcpp

from PIL import Image
from io import BytesIO
from datetime import datetime


# ---------------------------------------------------------
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# ---------------------------------------------------------
st.set_page_config(
    page_title="Local Items Price",
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
# MARKET
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
# SESSION STATE
# ---------------------------------------------------------
if "records" not in st.session_state:
    st.session_state.records = []

if "current_barcode" not in st.session_state:
    st.session_state.current_barcode = None

if "last_saved" not in st.session_state:
    st.session_state.last_saved = False

if "scan_counter" not in st.session_state:
    st.session_state.scan_counter = 0

if "entry_counter" not in st.session_state:
    st.session_state.entry_counter = 0


# ---------------------------------------------------------
# ΤΙΤΛΟΣ
# ---------------------------------------------------------
st.title("📱 Καταγραφή Τιμών")

st.caption(
    "Σκάναρε το barcode και καταχώρησε market και τιμή."
)


# ---------------------------------------------------------
# ΜΕΤΑ ΤΗΝ ΑΠΟΘΗΚΕΥΣΗ
# ---------------------------------------------------------
if st.session_state.last_saved:

    st.success("✅ Η τιμή αποθηκεύτηκε!")

    if st.button(
        "📷 Νέο scan",
        type="primary",
        use_container_width=True
    ):

        st.session_state.last_saved = False
        st.session_state.current_barcode = None
        st.session_state.scan_counter += 1
        st.session_state.entry_counter += 1

        st.rerun()


# ---------------------------------------------------------
# ΚΑΜΕΡΑ
# ---------------------------------------------------------
if not st.session_state.last_saved:

    photo = st.camera_input(
        "📷 Σκάναρε το barcode",
        key=f"camera_{st.session_state.scan_counter}"
    )


    # -----------------------------------------------------
    # ΑΝΑΓΝΩΣΗ BARCODE
    # -----------------------------------------------------
    if photo is not None:

        image = Image.open(photo)

        try:

            results = zxingcpp.read_barcodes(image)

            if len(results) == 0:

                st.warning(
                    "⚠️ Δεν μπόρεσα να διαβάσω barcode. "
                    "Προσπάθησε ξανά πιο κοντά και με καλό φωτισμό."
                )

            else:

                barcode = results[0].text.strip()

                st.info(
                    f"🔎 Barcode που διαβάστηκε: {barcode}"
                )

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

        except Exception as e:

            st.error(
                "❌ Παρουσιάστηκε πρόβλημα "
                "κατά την ανάγνωση του barcode."
            )


# ---------------------------------------------------------
# ΠΡΟΪΟΝ + MARKET + ΤΙΜΗ
# ---------------------------------------------------------
if (
    st.session_state.current_barcode
    and not st.session_state.last_saved
):

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


    # -----------------------------------------------------
    # MARKET
    # -----------------------------------------------------
    market = st.selectbox(
        "🏪 Επιλογή Market",
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
            st.session_state.last_saved = True

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
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )
