import streamlit as st

from module.db import DBController


def show_setting_page(db: DBController) -> None:
    """設定ページを表示します。"""
    st.subheader('設定')

    with st.form('update_account_form', border=False):
        user = db.get_user(st.session_state['user_id'])

        username = st.text_input('ユーザー名', value=user['username'], key='username')
        password = st.text_input('パスワード', value=user['password'], type='password', key='password')
        closing_day = st.number_input('締め日', min_value=1, max_value=31, value=user['closing_day'], step=1, key='closing_day')
        goal_amount = st.number_input('目標金額', value=user['goal_amount'], key='goal_amount')

        if st.form_submit_button('変更', type='primary'):
            if len(username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(password) == 0:
                st.error('パスワードが入力されていません')
            else:
                if db.update_user(st.session_state['user_id'], username, password, closing_day, goal_amount):
                    st.success(f'ユーザー名{username}の登録情報が変更されました')
                else:
                    st.error(f'ユーザー名{username}は既に存在します')
