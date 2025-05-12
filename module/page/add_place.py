import streamlit as st

from module.db import DBController


def show_add_place_page(db: DBController) -> None:
    """勤務先追加ページを表示します。"""
    st.subheader('勤務先追加')

    with st.form('add_place_form', border=False):
        add_place = st.text_input('追加する勤務先を入力してください', key='add_place')

        if st.form_submit_button('追加', type='primary'):
            if len(add_place) == 0:
                st.error('勤務先が入力されていません')
            else:
                if db.add_place(st.session_state['user_id'], add_place):
                    st.success(f'勤務先{add_place}が登録されました')
                else:
                    st.error(f'勤務先{add_place}は既に存在します')
