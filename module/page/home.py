from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

from module.db import DBController


def show_home_page(
    db: DBController,
    closing_day: int,
    goal_amount: int,
    limit_mount: int,
    pie_fontpath: str
) -> None:
    """ホームページを表示します。"""
    today = datetime.today()

    start_datetime, end_datetime = _get_date_period(today, closing_day)
    start_date_str = datetime.strftime(start_datetime, '%Y/%m/%d')
    end_date_str = datetime.strftime(end_datetime, '%Y/%m/%d')

    current_amount = db.get_amount(st.session_state['user_id'], start_datetime, today)
    estimated_amount = db.get_amount(st.session_state['user_id'], start_datetime, end_datetime)
    year_amount = db.get_amount(st.session_state['user_id'], datetime(today.year, 1, 1, 0, 0, 0), today)

    next_shift = db.get_next_shift(st.session_state['user_id'], today)

    st.subheader('ホーム')

    if st.button('ログアウト', type='primary', key='logout_btn'):
        st.session_state.clear()
        st.rerun()

    _display_pie_chart(
        current_amount,
        estimated_amount,
        goal_amount,
        start_date_str,
        end_date_str,
        pie_fontpath,
    )

    st.markdown(
        f'<div style="text-align: center; font-size: 28px; font-weight: bold;">{limit_mount:,}円まで残り{limit_mount - year_amount:,}円</div>',
        unsafe_allow_html=True
    )

    if next_shift is None:
        st.markdown(
            '<div style="text-align: center; font-size: 28px; font-weight: bold;">次回の出勤予定なし</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="text-align: center; font-size: 28px; font-weight: bold;">次回の出勤日は{next_shift.strftime("%Y/%m/%d")}</div>',
            unsafe_allow_html=True
        )


def _get_date_period(today: datetime, closing_day: int) -> tuple[datetime, datetime]:
    """指定された日付と締め日を基に、開始日と終了日を取得します。"""
    this_month_limit_date = _get_valid_date_for_month(today.year, today.month, closing_day)

    if today > this_month_limit_date:
        start_date = this_month_limit_date + timedelta(days=1)
        end_date = _get_valid_date_for_month(
            today.year if today.month != 12 else today.year + 1,
            today.month + 1 if today.month != 12 else 1,
            closing_day,
        ).replace(hour=23, minute=59, second=59)
    else:
        start_date = _get_valid_date_for_month(
            today.year if today.month != 1 else today.year - 1,
            today.month - 1 if today.month != 1 else 12,
            closing_day,
        ) + timedelta(days=1)
        end_date = this_month_limit_date.replace(hour=23, minute=59, second=59)

    return start_date, end_date


def _get_valid_date_for_month(year: int, month: int, closing_day: int) -> datetime:
    """指定された年、月、および締め日から有効な日付を取得します。"""
    day = closing_day
    while True:
        try:
            return datetime(year=year, month=month, day=day)
        except ValueError:
            day -= 1


def _display_pie_chart(
    current_amount: int,
    estimated_amount: int,
    goal_amount: int,
    start_date: str,
    end_date: str,
    pie_fontpath: str,
) -> None:
    """円グラフを表示します。"""
    achievement_rate = (current_amount / goal_amount) * 100

    achievement_rate = 100 if achievement_rate > 100 else achievement_rate

    sizes = [achievement_rate, 100 - achievement_rate]
    colors = ['#52b338', '#e2e9d9']
    wedge = {'width' : 0.1}

    plt.pie(sizes, colors=colors, wedgeprops=wedge, startangle=90, counterclock=False)

    fontpath = pie_fontpath
    font_prop = fm.FontProperties(fname=fontpath)

    plt.text(0, 0.5, f'{start_date} - {end_date}', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, 0.35, f'目標金額 {goal_amount:,}円', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, 0.15, '今日までの給料', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, -0.05, f'{current_amount:,}円', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=20)
    plt.text(0, -0.3, '見込み額', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, -0.5, f'{estimated_amount:,}円', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=20)

    st.pyplot(plt)
