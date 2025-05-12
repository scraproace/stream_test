import streamlit as st

from module.const import CLOSING_DAY, GOAL_AMOUNT, LIMIT_AMOUNT, PIE_FONTPATH
from module.db import DBController
from module.page import show_home_page, show_add_place_page, show_login_page, show_create_account_page, show_shift_page


def main():
    """
    メイン関数。シフト管理アプリケーションのエントリーポイント。
    この関数は、データベースコントローラを初期化し、ユーザーのログイン状態に応じて
    適切なメニューを表示します。選択されたメニューに基づいて、対応するページを表示します。
    メニューオプション:
    - ホーム: ホームページを表示
    - 勤務先追加: 勤務先追加ページを表示
    - シフト: シフトページを表示
    - ログイン: ログインページを表示
    - アカウント作成: アカウント作成ページを表示
    """
    db = DBController()

    st.title('シフト管理')

    if 'is_login' in st.session_state:
        menu = ['ホーム', '勤務先追加', 'シフト']
    else:
        menu = ['ログイン', 'アカウント作成']

    choice = st.sidebar.selectbox('メニュー', menu)

    if choice == 'ホーム':
        show_home_page(db, CLOSING_DAY, GOAL_AMOUNT, LIMIT_AMOUNT, PIE_FONTPATH)
    elif choice == '勤務先追加':
        show_add_place_page(db)
    elif choice == 'シフト':
        show_shift_page(db)
    elif choice == 'ログイン':
        show_login_page(db)
    elif choice == 'アカウント作成':
        show_create_account_page(db)


if __name__ == '__main__':
    main()
