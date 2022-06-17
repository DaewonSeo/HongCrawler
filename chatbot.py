
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_chat import message
from sentence_transformers import SentenceTransformer
import json
import pandas as pd
import streamlit as st


@st.cache(hash_funcs={'_json.Scanner': hash}, allow_output_mutation=True)
def cached_model():
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    return model


@st.cache(hash_funcs={'_json.Scanner': hash}, allow_output_mutation=True)
def get_dataset():
    df = pd.read_csv('data/board_log.csv')
    df['embedding'] = df['embedding'].apply(json.loads)
    return df


model = cached_model()
df = get_dataset()

st.header('정치인 챗봇')
st.subheader('Hongbot(Beta)')
st.markdown("[소스코드](https://github.com/DaewonSeo/HongCrawler)")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

with st.form('form', clear_on_submit=True):
    user_input = st.text_input('홍봇에게 질문해보세요: ', '')
    submitted = st.form_submit_button('전송')

if submitted and user_input:
    embedding = model.encode(user_input)

    df['similarity'] = df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())
    answer = df.loc[df['similarity'].idxmax()]

    st.session_state.past.append(user_input)
    st.session_state.generated.append(answer['A'])
    print(answer['Q'])

for i in range(len(st.session_state['past'])):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    if len(st.session_state['generated']) > i:
        message(st.session_state['generated'][i], key=str(i) + '_bot')