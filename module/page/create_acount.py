import streamlit as st

from module.db import DBController


def show_create_account_page(db: DBController) -> None:
    """アカウント作成ページを表示します。"""
    st.subheader('アカウント作成')

    with st.form('create_account_form', border=False):
        create_username = st.text_input('ユーザー名を入力してください', key='create_username')
        create_password = st.text_input('パスワードを入力してください', type='password', key='create_password')

        if st.form_submit_button('作成', type='primary'):
            if len(create_username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(create_password) == 0:
                st.error('パスワードが入力されていません')
            else:
                if db.add_user(create_username, create_password):
                    st.success(f'ユーザー名{create_username}が登録されました')
                else:
                    st.error(f'ユーザー名{create_username}は既に存在します')
