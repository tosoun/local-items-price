import streamlit as st
import pandas as pd

from streamlit_qrcode_scanner import qrcode_scanner
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
# SESSION STATE
# ---------------------------------------------------------
if "records" not in st.session_state:
    st.session_state.records = []

if "current_barcode" not in st.session_state:
    st.session_state.current_barcode = None

if "scanner_counter" not in st.session_state:
    st.session_state.scanner_counter = 0

if "last_saved" not in st.session_state:
    st.session_state.last_saved = False


# ---------------------------------------------------------
# ΤΙΤΛΟΣ
# ---------------------------------------------------------
st.title("📱 Καταγραφή Τιμών")

st.caption(
    "Σκάναρε το barcode του προϊόντος και καταχώρησε την τιμή."
)


# ---------------------------------------------------------
# ΜΗΝΥΜΑ ΜΕΤΑ ΤΗΝ ΑΠΟΘΗΚΕΥΣΗ
# ---------------------------------------------------------
if st.session_state.last_saved:

    st.success("✅ Η τιμή αποθηκεύτηκε.")

    if st.button(
        "📷 Νέο scan",
        type="primary",
        use_container_width=True
    ):
        st.session_state.last_saved = False
        st.session_state.current_barcode = None
        st.session_state.scanner_counter += 1

        st.rerun()


# ---------------------------------------------------------
# SCANNER
# ---------------------------------------------------------
if not st.session_state.last_saved:

    st.subheader("📷 Σκάναρε το barcode")

    barcode_result = qrcode_scanner(
        key=f"scanner_{st.session_state.scanner_counter}"
    )


    # -----------------------------------------------------
    # ΕΛΕΓΧΟΣ BARCODE
    # -----------------------------------------------------
    if barcode_result:

        barcode = str(barcode_result).strip()

        if barcode != st.session_state.current_barcode:

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
# ΕΜΦΑΝΙΣΗ ΠΡΟΪΟΝΤΟΣ
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
    # ΤΙΜΗ
    # -----------------------------------------------------
    price = st.number_input(
        "💶 Τιμή (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f"
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
