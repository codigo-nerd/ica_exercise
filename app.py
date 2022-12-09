import streamlit as st
import pandas as pd
#import joblib
from keybert import KeyBERT

st.set_page_config(page_title='Medical/Device Keyword Extractor', layout='wide')
st.sidebar.title('Medical/Device Keyword Extractor')

#load items
#model = joblib.load('saved_kb.pkl')
model = KeyBERT()
conditions = []
f = open("conditions.txt", "r")
for x in f:
    conditions.append(x[:-1])
f.close()

def convert_df(df):
     return df.to_csv().encode('utf-8')

selection = st.sidebar.selectbox('Select an upload method',['','Sentence','Dataset'],0)

if selection == 'Sentence':
    sentence = st.sidebar.text_input('Insert sentence')
    if sentence != '':
        results = model.extract_keywords(sentence, keyphrase_ngram_range=(1, 1), nr_candidates=10, top_n=10)
        st.markdown('<p style=" color:#48D1CC; font-size: 25px;"><b>Text:</b></p>',unsafe_allow_html=True,)
        st.markdown(sentence)
        st.markdown('<p style=" color:#48D1CC; font-size: 25px;"><b>Results:</b></p>',unsafe_allow_html=True,)
        
        phrases = model.extract_keywords(sentence, keyphrase_ngram_range=(4, 4), nr_candidates=10, top_n=5)
        devices = []
        medical = []
        for i in results:
            if i[0] in conditions:
                medical.append(i)
            else:
                devices.append(i)
        
        df_res1 = pd.DataFrame(devices, columns =['dev_Keyword','dev_Score'])
        df_res2 = pd.DataFrame(medical, columns =['med_Keyword','med_Score'])
        df_res3 = pd.DataFrame(phrases, columns =['sentences','sent_Score'])
        df_res = pd.concat([df_res1, df_res2, df_res3],axis=1)

        row1, row1_spacer, row2 = st.columns((6,0.1,1.5))
        with row1:
            st.write(df_res)
            st.markdown(" ")
            st.markdown(" ")
        
        with row2:
            st.markdown('<p style=" color:#48D1CC; font-size: 25px;"><b>Download Options:</b></p>',unsafe_allow_html=True,)

            st.markdown('<p style=" color:#48D1CC; font-size: 15px;"><b>Option 1</b></p>',unsafe_allow_html=True,)
            
            df_res = convert_df(df_res)
            
            st.download_button(
            label="Download data as CSV",
            data=df_res,
            file_name='key_word_results.csv',
            mime='text/csv',
            )
            st.markdown('<p style=" color:#48D1CC; font-size: 15px;"><b>Option 1</b></p>',unsafe_allow_html=True,)
            st.download_button('Download data as text', str(results))

        

elif selection == 'Dataset':
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    
    if uploaded_file is not None:
        
        st.warning('Extensive datasets might take several minutes to process')
        dataframe = pd.read_csv(uploaded_file)
        dataframe[' '] = 'placeholder'
        column_names = list(dataframe.columns)
        column_name = st.selectbox('Choose the column for keyword extraction', column_names,(len(dataframe.columns)-1))

        if column_name != ' ':

            results = model.extract_keywords(dataframe[f'{column_name}'], keyphrase_ngram_range=(1, 1), nr_candidates=10, top_n=10)
            phrases = model.extract_keywords(dataframe[f'{column_name}'], keyphrase_ngram_range=(4, 4), nr_candidates=10, top_n=5)

            dev = []
            dev_s = []
            med = []
            med_s = []

            for i in results:
                temp_dev = []
                temp_dev_s = []
                temp_med = []
                temp_med_s = []
                for j in i:
                    if j[0] in conditions:
                        temp_med.append(j[0])
                        temp_med_s.append(j[1])
                    else:
                        temp_dev.append(j[0])
                        temp_dev_s.append(j[1])
                    
                    if len(temp_dev) == 10:
                        temp_med.append('None')
                        temp_med_s.append('None')
            
                    if len(temp_med) == 10:
                        temp_dev.append('None')
                        temp_dev_s.append('None')

                dev.append(temp_dev)
                dev_s.append( temp_dev_s)
                med.append(temp_med)
                med_s.append(temp_med_s)
            
            df = pd.DataFrame()
            df['original_text'] = dataframe[f'{column_name}']
            df['device_keywords'] = dev
            df['dev_keywords_scores'] = dev_s
            df['medical_keywords'] = med
            df['med_keywords_scores'] = med_s

            others_phrases = []
            others_scores = []

            for i in phrases:
    
                phrases_temp = []
                scores_temp = []

                for j in i:
                    phrases_temp.append(j[0])
                    scores_temp.append(j[1])
                    
                others_phrases.append(phrases_temp)
                others_scores.append(scores_temp)           
            
            df['phrases'] = others_phrases
            df['phrases_scores'] = others_scores

            st.write(df)

            st.markdown('<p style=" color:#48D1CC; font-size: 25px;"><b>Download:</b></p>',unsafe_allow_html=True,)
            
            df = convert_df(df)
            
            st.download_button(
            label="Download data as CSV",
            data=df,
            file_name='key_word_results.csv',
            mime='text/csv',
            )