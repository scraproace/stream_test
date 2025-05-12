import streamlit as st

from module.db import DBController


def show_login_page(db: DBController) -> None:
    """ログインページを表示します。"""
    st.subheader('ログイン画面')

    with st.form('login_form', border=False):
        login_username = st.text_input('ユーザー名を入力してください', key='login_username')
        login_password = st.text_input('パスワードを入力してください', type='password', key='login_password')

        if st.form_submit_button('ログイン', type='primary'):
            if len(login_username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(login_password) == 0:
                st.error('パスワードが入力されていません')
            else:
                user_id = db.login(login_username, login_password)

                if user_id:
                    st.session_state['is_login'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['shifts'] = None
                    st.rerun()
                else:
                    st.error('ユーザー名またはパスワードが間違っています')
