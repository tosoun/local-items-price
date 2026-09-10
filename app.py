import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from streamlit_qrcode_scanner import qrcode_scanner
from io import BytesIO
from datetime import datetime
import base64
import wave
import math
import struct


# ---------------------------------------------------------
# ΡΥΘΜΙΣΕΙΣ
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

if "last_barcode" not in st.session_state:
    st.session_state.last_barcode = None

if "last_saved" not in st.session_state:
    st.session_state.last_saved = False

if "scan_number" not in st.session_state:
    st.session_state.scan_number = 0


# ---------------------------------------------------------
# ΔΗΜΙΟΥΡΓΙΑ BEEP WAV
# ---------------------------------------------------------
def create_beep():

    sample_rate = 44100
    duration = 0.18
    frequency = 1250
    volume = 0.8

    buffer = BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        samples = int(sample_rate * duration)

        for i in range(samples):

            value = int(
                32767
                * volume
                * math.sin(
                    2 * math.pi * frequency * i / sample_rate
                )
            )

            wav.writeframes(
                struct.pack("<h", value)
            )

    return base64.b64encode(
        buffer.getvalue()
    ).decode()


BEEP_DATA = create_beep()


# ---------------------------------------------------------
# ΑΥΤΟΜΑΤΟ BEEP
# ---------------------------------------------------------
def play_beep():

    components.html(
        f"""
        <audio
            id="scanBeep"
            autoplay
            playsinline
            preload="auto"
        >
            <source
                src="data:audio/wav;base64,{BEEP_DATA}"
                type="audio/wav"
            >
        </audio>

        <script>

        const sound =
            document.getElementById("scanBeep");

        sound.volume = 1.0;

        sound.currentTime = 0;

        sound.play()
            .then(() => {{
                console.log("BEEP OK");
            }})
            .catch((error) => {{
                console.log(
                    "Safari blocked autoplay",
                    error
                );
            }});

        </script>
        """,
        height=1
    )


# ---------------------------------------------------------
# ΤΙΤΛΟΣ
# ---------------------------------------------------------
st.title("📱 Καταγραφή Τιμών")

st.caption(
    "Σκάναρε το barcode και καταχώρησε market και τιμή."
)


# ---------------------------------------------------------
# SCANNER
# ---------------------------------------------------------
st.subheader("📷 Scanner")

barcode_result = qrcode_scanner(
    key="barcode_scanner"
)


# ---------------------------------------------------------
# ΜΕΤΑ ΤΗΝ ΑΠΟΘΗΚΕΥΣΗ
# ---------------------------------------------------------
if st.session_state.last_saved:

    st.success(
        "✅ Η τιμή αποθηκεύτηκε!"
    )

    if st.button(
        "📷 Νέο scan",
        type="primary",
        use_container_width=True
    ):

        st.session_state.last_saved = False
        st.session_state.current_barcode = None
        st.session_state.last_barcode = None
        st.session_state.scan_number += 1

        st.rerun()


# ---------------------------------------------------------
# ΑΝΑΓΝΩΡΙΣΗ BARCODE
# ---------------------------------------------------------
elif barcode_result:

    barcode = str(
        barcode_result
    ).strip()

    if barcode != st.session_state.last_barcode:

        st.session_state.last_barcode = barcode

        if barcode in PRODUCTS:

            st.session_state.current_barcode = barcode

            # -----------------------------
            # ΑΥΤΟΜΑΤΟ BEEP
            # -----------------------------
            play_beep()

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
# ΠΡΟΪΟΝ
# ---------------------------------------------------------
if (
    st.session_state.current_barcode
    and not st.session_state.last_saved
):

    barcode = st.session_state.current_barcode
    product = PRODUCTS[barcode]

    st.divider()

    st.subheader(
        "🛒 Προϊόν"
    )

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
        index=0
    )


    # -----------------------------------------------------
    # ΤΙΜΗ
    # -----------------------------------------------------
    price = st.number_input(
        "💶 Τιμή (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f",
        key="price_input"
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

    st.subheader(
        "📋 Καταχωρήσεις"
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
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )
