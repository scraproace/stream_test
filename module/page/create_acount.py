import streamlit as st

from module.db import DBController


def show_create_account_page(db: DBController) -> None:
    """アカウント作成ページを表示します。"""
    st.subheader('アカウント作成')

    with st.form('create_account_form', border=False):
        username = st.text_input('ユーザー名を入力してください', key='username')
        password = st.text_input('パスワードを入力してください', type='password', key='password')
        closing_day = st.number_input('締め日を入力してください', min_value=1, max_value=31, value=15, step=1, key='closing_day')
        goal_amount = st.number_input('目標金額を入力してください', value=100000, key='goal_amount')

        if st.form_submit_button('作成', type='primary'):
            if len(username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(password) == 0:
                st.error('パスワードが入力されていません')
            else:
                if db.add_user(username, password, closing_day, goal_amount):
                    st.success(f'ユーザー名{username}が登録されました')
                else:
                    st.error(f'ユーザー名{username}は既に存在します')
