from collections import namedtuple
import math
import pandas as pd
import streamlit as st
import pandas as pd
from io import BytesIO
from garmin_fit_sdk import Decoder, Stream

 

st.set_page_config(
    page_title="Driftline",
    page_icon="https://www.driftline.io/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.driftline.io/',
        'Report a bug': "https://www.driftline.io/contact",
        'About': "# Made by Driftline https://www.driftline.io/"
    }
)

st.markdown(
'''
<style>
.block-container{
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
</style>
''',
    unsafe_allow_html=True,
)
"""
### Driftline .fit to .xslx converter
"""


def main():
    st.session_state['excel'] = pd.DataFrame([1,2,3])
    st.session_state['uploaded'] = False

    uploaded_file = st.file_uploader(label = "Fit file uploader", type='.fit')
    if uploaded_file is not None:
        # To read file as bytes:
        try:
            stream = Stream.from_bytes_io(uploaded_file)
            decoder = Decoder(stream)
            messages, _ = decoder.read()
            df = pd.DataFrame.from_records(messages['record_mesgs'])
            date = pd.to_datetime(df['timestamp'])
            dateDiff = date - date[0]
            secs = dateDiff.astype(int)
            df.index = (secs/(10**9)).astype(int)
            df = df.drop(columns = ['timestamp'])
            st.session_state['excel'] = df
            st.session_state['uploaded'] = True
            print(df)
        except:
            print('failed')

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        st.session_state['excel'].to_excel(writer, sheet_name='Sheet1')
        writer.close()
        st.download_button(
            label='Download Excel File',
            data=buffer.getvalue(),
            file_name="streamlit_run.xlsx",
            mime='application/vnd.ms-excel',
            disabled = not bool(st.session_state['uploaded'])
        )



if __name__ == "__main__":
    main()