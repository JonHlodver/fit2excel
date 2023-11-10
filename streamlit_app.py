from collections import namedtuple
import math
import pandas as pd
import numpy as np
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
    st.session_state['excel'] = pd.DataFrame([])
    st.session_state['uploaded'] = False

    uploaded_files = st.file_uploader(label = "Fit file uploader:", type='.fit', accept_multiple_files=True)
    if uploaded_files is not None:
        # To read file as bytes:
        #try:
        for uploaded_file in uploaded_files:
            print(uploaded_file.name)
            stream = Stream.from_bytes_io(uploaded_file)
            decoder = Decoder(stream)
            messages, _ = decoder.read()
            data = pd.DataFrame.from_records(messages['record_mesgs'])
            filenumber = uploaded_file.name.split('_')[0]
            st.session_state['excel'] = add2df(data, st.session_state['excel'], filenumber)
            st.session_state['uploaded'] = True
        #except:
        #    print('failed')

    filename = st.text_input('Filename:', 'fit2excel')
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        st.session_state['excel'].to_excel(writer, sheet_name='Sheet1')
        writer.close()
        st.download_button(
            label='Download Excel File',
            data=buffer.getvalue(),
            file_name=filename+'.xlsx',
            mime='application/vnd.ms-excel',
            disabled = not bool(st.session_state['uploaded'])
        )

def add2df(data, dfOld, filenumber):
    date = pd.to_datetime(data['timestamp'])
    dateDiff = date - date[0]
    secs = dateDiff.astype(int)
    data.index = (secs/(10**9)).astype(int)
    if 'heart_rate' in data:
        if 'cadence' in data:
            data = data.loc[:, ['heart_rate', 'cadence']]
        else:
            data = data.loc[:, ['heart_rate']]
        df = spanTime(data)

        header = pd.MultiIndex.from_product([[filenumber],['hr','cadence']],names=['subject','measurement'])
        df.columns = header

        if dfOld.size != 0:
            dfOld = dfOld.join(df, how = 'outer')
        else:
            dfOld = df

    return dfOld



def spanTime(df):
    """
    if samples are missing for some timepoints: add them as None
    """
    length = int(df.index.to_series().iloc[-1])
    df = df[~df.index.duplicated(keep='first')]
    df = df.reindex(range(length + 1), fill_value=np.nan)
    return df


if __name__ == "__main__":
    main()