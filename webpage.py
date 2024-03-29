import streamlit as st
from supabase import create_client, Client
from gotrue.errors import AuthApiError

# Supabase 연결 설정
url = "https://yuijzwcqrdzhrnbmypxu.supabase.co"
key = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1aWp6d2NxcmR6aHJuYm15cHh1Iiwicm"
       "9sZSI6ImFub24iLCJpYXQiOjE3MDgzMzQzNTcsImV4cCI6MjAyMzkxMDM1N30.F7oejhngT32UV0bZBLKlxLe6cMF8OO_YffS6nhS3fFY")
supabase: Client = create_client(url, key)


# 로그인 여부 확인
def check_login():
    if "user" not in st.session_state:
        st.session_state.user = None
    return st.session_state.user


# 로그인 기능
def login():
    email = st.text_input("아이디:") + '@n'
    password = st.text_input("비밀번호:", type="password")
    if st.button("로그인"):
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = result.user.id
            st.success(f"로그인 성공: {email[:-2]}")
            st.session_state.login = True
            st.rerun()
        except AuthApiError as e:
            st.error(f"로그인 실패...: {e}")
            return False
    if st.session_state.signup:
        signup_email = st.text_input("아이디:", key=1) + '@n'
        signup_password = st.text_input("비밀번호:", type="password", key=2)
        try:
            if st.button("회원가입", key=3):
                if signup_email and signup_password:
                    supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                    result = supabase.auth.sign_in_with_password({"email": signup_email, "password": signup_password})
                    st.session_state.user = result.user.id
                    st.success(f"회원가입 성공: {signup_email[:-2]}")
                    st.session_state.login = True
                st.session_state.signup = False
                st.rerun()
        except AuthApiError as e:
            st.error(f"회원가입 실패: {e}")
    elif st.button("회원가입"):
        st.session_state.signup = True
        st.rerun()

# 로그아웃 기능
def logout():
    st.session_state.user = None
    with col[0]:
        st.success("로그아웃 되었습니다~")


# 글 작성 기능
def write_post():
    if not check_login():
        st.warning("로그인이 필요합니다!")
        return
    with col[0]:
        title = st.text_input("제목:")
        content = st.text_area("내용:", height=200)
        if st.button("저장"):
            try:
                if title or content:
                    supabase.table("Post").insert(
                        [{"Title": title, "Body": content, "user_id": st.session_state.user}]
                    ).execute()
                    st.success("작성 완료!")
                st.session_state.write = False
                st.rerun()
            except Exception as e:
                st.error(f"글 작성 실패...: {e}")


# 사용자의 글만 조회하는 기능
def list_user_posts():
    if not check_login():
        st.warning("로그인이 필요합니다!")
        return

    user_posts = supabase.table("Post").select("*").execute()
    option = st.selectbox("글 목록", user_posts.data, index=None, format_func=lambda post: post["Title"])
    if option:
        if option["courage"]:
            with st.expander("메시지가 있습니다!"):
                st.markdown('''**''' + option["courage"] + '''**''')
        editted = st.text_area('', option["Body"], height=200)
        if st.button("완료"):
            try:
                supabase.table("Post").update({"Body": editted}).eq("Title", option["Title"]).execute()
                st.session_state.edit = False
                st.success(f"글 수정 완료!")
                st.rerun()
            except Exception as e:
                st.error(f"글 수정 실패...: {e}")
    # for post in user_posts:
    #     st.write(f"**{post['title']}** - 작성자: {post['user_id']}")

if "login" not in st.session_state:
    st.session_state.login = False
if "write" not in st.session_state:
    st.session_state.write = False
if "edit" not in st.session_state:
    st.session_state.edit = False
if "signup" not in st.session_state:
    st.session_state.signup = False
if "feedback" not in st.session_state:
    st.session_state.feedback = False

# 메인 페이지
st.title("고민 상담소")
col = st.columns([4, 1])
if st.session_state.login:
    with col[1]:
        if st.button("로그아웃"):
            logout()
            st.session_state.login = False
            st.rerun()
        elif st.session_state.feedback:
            with col[0]:
                feedback = st.text_area("피드백")
                if st.button("완료"):
                    if feedback:
                        supabase.table("Feedback").insert(
                        [{"feedback": feedback, "user_id": st.session_state.user}]
                        ).execute()
                    st.session_state.feedback = False
                    st.rerun()
        elif st.button("피드백"):
            st.session_state.feedback = True
            st.rerun()
    with col[0]:
        if st.session_state.write:
            write_post()
        elif st.button("작성"):
            st.session_state.write = True
            st.rerun()
        elif st.session_state.edit:
            list_user_posts()
        elif st.button("조회 / 수정"):
            st.session_state.edit = True
            st.rerun()
else:
    login()