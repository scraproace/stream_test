from datetime import datetime, time, timedelta

import streamlit as st
import streamlit_calendar as st_calendar

from module.db import DBController


def show_shift_page(db: DBController) -> None:
    """シフトページを表示します。"""
    if st.session_state['shifts'] is None:
        st.session_state['shifts'] = db.get_shifts(st.session_state['user_id'])

    events = []
    for shift in st.session_state['shifts']:
        events.append({
            'id': shift['id'],
            'title': shift['title'],
            'start': datetime.strftime(shift['start_datetime'], '%Y-%m-%dT%H:%M:%S'),
            'end': datetime.strftime(shift['end_datetime'], '%Y-%m-%dT%H:%M:%S'),
        })

    st.subheader('シフト')

    if st.button('追加', type='primary', key='add_shift_btn'):
        _show_add_form(db)

    options = {
        'initialView': 'dayGridMonth',
        'titleFormat': {
            'year': 'numeric',
            'month': '2-digit',
            'day': '2-digit'
        },
        'locale': 'ja',
    }

    calender_event = st_calendar.calendar(events=events, options=options)

    if calender_event:
        if calender_event['callback'] == 'eventClick':
            selected_shift_id = int(calender_event['eventClick']['event']['id'])
            selected_shift = [shift for shift in st.session_state['shifts'] if shift['id'] == selected_shift_id][0]
            _show_detail(selected_shift, db)


@st.dialog('シフト追加')
def _show_add_form(db: DBController):
    """シフト追加ダイアログを表示します。"""
    places = db.get_places(st.session_state['user_id'])

    if places:
        is_repeat = st.checkbox('週次登録', key='is_repeat')

        with st.form('add_shift_form', border=False):
            shift_place = st.selectbox('勤務先を選択してください', options=places, key='shift_place')
            shift_title = st.text_input('タイトルを入力してください', key='shift_title')
            shift_start_date = st.date_input('開始日付を入力してください', value=datetime.today(), key='shift_start_date')
            shift_start_time = st.time_input('開始時刻を入力してください', value=time(9, 0), key='shift_start_time', step=300)
            shift_end_date = st.date_input('終了日付を入力してください', value=datetime.today(), key='shift_end_date')
            shift_end_time = st.time_input('終了時刻を入力してください', value=time(17, 0), key='shift_end_time', step=300)

            if is_repeat:
                repeat_end_date = st.date_input('最終日付(週次)を入力してください', value=datetime.today(), key='repeat_end_date')

            shift_break_time = st.time_input('休憩時間を入力してください', value=time(0, 0), key='shift_break_time', step=300)
            shift_hourly_wage = st.number_input('時給(円)を入力してください', value=1000, key='shift_hourly_wage', step=1)

            if st.form_submit_button('追加', type='primary'):
                if len(shift_title) == 0:
                    st.error('タイトルが入力されていません')
                else:
                    shift_start_datetime = datetime.combine(shift_start_date, shift_start_time)
                    shift_end_datetime = datetime.combine(shift_end_date, shift_end_time)

                    if shift_start_datetime >= shift_end_datetime:
                        st.error('開始日時は終了日時よりも早く設定してください')
                    else:
                        if is_repeat:
                            if shift_start_date > repeat_end_date:
                                st.error('開始日時は最終日付(週次)よりも早く設定してください')
                            else:
                                while shift_start_date <= repeat_end_date:
                                    if db.add_shift(
                                        st.session_state['user_id'],
                                        shift_place,
                                        shift_title,
                                        shift_start_datetime,
                                        shift_end_datetime,
                                        shift_break_time,
                                        shift_hourly_wage,
                                        is_upadate=True,
                                    ):
                                        shift_start_date += timedelta(days=7)
                                        shift_end_date += timedelta(days=7)
                                        shift_start_datetime = datetime.combine(shift_start_date, shift_start_time)
                                        shift_end_datetime = datetime.combine(shift_end_date, shift_end_time)
                                else:
                                    st.session_state['shifts'] = None
                                    st.rerun()
                        else:
                            if db.add_shift(
                                st.session_state['user_id'],
                                shift_place,
                                shift_title,
                                shift_start_datetime,
                                shift_end_datetime,
                                shift_break_time,
                                shift_hourly_wage,
                            ):
                                st.session_state['shifts'] = None
                                st.rerun()
                            else:
                                st.error('その時間はシフトが既に存在します')
    else:
        st.error('勤務先が登録されていません')


@st.dialog('シフト詳細')
def _show_detail(shift: dict, db: DBController):
    """シフト詳細ダイアログを表示します。"""
    st.write(f"勤務先：{shift['place']}")
    st.write(f"タイトル：{shift['title']}")
    st.write(f"開始日時：{datetime.strftime(shift['start_datetime'], '%Y/%m/%d %H:%M')}")
    st.write(f"終了日時：{datetime.strftime(shift['end_datetime'], '%Y/%m/%d %H:%M')}")
    st.write(f"休憩時間：{time.strftime(shift['break_time'], '%H:%M')}")
    st.write(f"時給(円)：{shift['hourly_wage']}")

    if st.button('削除', type='primary', key='delete_shift_btn'):
        db.delete_shift(shift['id'])
        st.session_state['shifts'] = None
        st.rerun()
