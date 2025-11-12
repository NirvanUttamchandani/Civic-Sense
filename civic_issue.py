import streamlit as st
import mysql.connector
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import io
import base64
import os

# --- PAGE CONFIGURATION ---

st.set_page_config(
    page_title="PMC Civic Portal",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Function to encode image for CSS ---

try:
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the image file
    hero_image_path = os.path.join(script_dir, "hero-civic.jpg")
except NameError:
    # Fallback if __file__ is not defined
    hero_image_path = "hero-civic.jpg"

@st.cache_data  # Cache the image data
def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return None


hero_image_base64 = get_image_base64(hero_image_path)

def load_react_ui_css():
    global hero_image_base64
    hero_background_css = (
        f"url('data:image/jpeg;base64,{hero_image_base64}')"
        if hero_image_base64
        else "linear-gradient(135deg, hsl(222 47% 31%), hsl(221 83% 53%))"
    )

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {{
            --background: 218 28% 97%; --foreground: 222 47% 11%;
            --card: 0 0% 100%; --card-foreground: 222 47% 11%;
            --popover: 0 0% 100%; --popover-foreground: 222 47% 11%;
            --primary: 221 83% 53%; --primary-foreground: 210 40% 98%;
            --primary-dark: 222 47% 31%; --primary-glow: 217 91% 78%;
            --secondary: 210 40% 96%; --secondary-foreground: 222 47% 11%;
            --muted: 210 40% 96%; --muted-foreground: 215 16% 47%;
            --accent: 188 95% 43%; --accent-foreground: 0 0% 100%; --accent-light: 188 95% 93%;
            --destructive: 0 84% 60%; --destructive-foreground: 210 40% 98%;
            --success: 142 71% 45%; --success-foreground: 0 0% 100%; --success-light: 142 76% 94%;
            --warning: 28 100% 53%; --warning-foreground: 0 0% 100%; --warning-light: 28 100% 95%;
            --border: 214 32% 91%; --input: 214 32% 91%; --ring: 221 83% 53%; --radius: 0.75rem;
            --gradient-primary: linear-gradient(135deg, hsl(var(--primary-dark)), hsl(var(--primary)));
            --gradient-accent: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent)));
            --gradient-hero: linear-gradient(135deg, hsl(var(--primary-dark)) 0%, hsl(var(--primary)) 50%, hsl(var(--accent)) 100%);
            --shadow-sm: 0 2px 8px rgba(30, 58, 138, 0.06); --shadow-md: 0 8px 24px rgba(30, 58, 138, 0.1);
            --shadow-lg: 0 16px 48px rgba(30, 58, 138, 0.15); --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{ font-family: 'Inter', sans-serif; border-color: hsl(var(--border)); box-sizing: border-box; }}
        body {{ margin: 0; background-color: hsl(var(--background)); color: hsl(var(--foreground)); }}
        .stApp {{ background-color: hsl(var(--background)); }}
        #MainMenu, footer {{ visibility: hidden; }}
        div[data-testid="stAppDeployButton"] {{ display: none; }}

        .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        .container {{ max-width: 1140px; margin: auto; padding: 0 1rem; }}

        /* --- Sidebar --- */
        [data-testid="stSidebar"] {{ background-color: #0c1c38; border-right: none; }}
        [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
        [data-testid="stSidebar"] .stButton>button {{
            background: var(--gradient-primary); color: hsl(var(--primary-foreground));
            border: none; border-radius: 0.5rem; padding: 0.6rem 1.25rem;
            font-weight: 600; font-size: 0.95rem; transition: var(--transition-smooth);
            box-shadow: var(--shadow-sm);
        }}
        [data-testid="stSidebar"] .stButton>button:hover {{
            opacity: 0.9; transform: translateY(-1px); box-shadow: var(--shadow-md);
        }}

        /* --- Hero Section --- */
        .hero-section {{
            position: relative; overflow: hidden;
            padding: 6rem 1rem 8rem 1rem;
            background-image: {hero_background_css};
            background-size: cover; background-position: center center;
        }}
        .hero-overlay {{
            position: absolute; inset: 0;
            background: linear-gradient(135deg, hsla(222,47%,31%,0.85) 0%, hsla(221,83%,53%,0.75) 50%, hsla(188,95%,43%,0.65) 100%);
            z-index: 1;
        }}
        .hero-content {{
            position: relative; z-index: 2; max-width: 900px; margin: auto; text-align: center;
        }}
        .hero-content h1 {{
            font-size: 3.5rem; font-weight: 800; color: white; margin-bottom: 1.5rem; line-height: 1.2;
        }}
        .hero-content p {{
            font-size: 1.25rem; color: rgba(255,255,255,0.9);
            margin-bottom: 2.5rem; max-width: 600px; margin: auto;
        }}
        .hero-buttons-container {{ display: flex; gap: 1rem; justify-content: center; }}
        #hero_start button {{
            background: var(--gradient-accent) !important; color: white !important;
            box-shadow: var(--shadow-glow) !important; padding: 0.75rem 2rem !important;
            font-size: 1.1rem !important; font-weight: 700 !important;
            border-radius: var(--radius) !important; border: none !important;
        }}
        #hero_dash button {{
            background-color: rgba(255,255,255,0.1) !important; backdrop-filter: blur(5px) !important;
            color: white !important; border: 1px solid white !important;
            padding: 0.75rem 2rem !important; font-size: 1.1rem !important; font-weight: 700 !important;
            border-radius: var(--radius) !important;
        }}
        #hero_dash button:hover {{ background-color: white !important; color: hsl(var(--primary)) !important; }}

        /* --- Stats Section --- */
        .stats-section {{ background-color: hsl(var(--background)); padding: 3rem 0; }}
        .metric-card {{ transition: var(--transition-smooth); text-align: center; }}
        .metric-card:hover {{ transform: translateY(-5px); box-shadow: var(--shadow-lg); }}
        .metric-icon-wrapper {{
            width: 3.5rem; height: 3.5rem; border-radius: var(--radius);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 1rem; font-size: 1.75rem; margin: auto;
            background: var(--gradient-primary); color: white;
        }}
        .metric-value {{ font-size: 2.25rem; font-weight: 800; color: hsl(var(--foreground)); }}
        .metric-label {{ font-size: 0.9rem; font-weight: 600; color: hsl(var(--muted-foreground)); }}

        /* --- Features Section --- */
        .features-section {{ background-color: hsl(var(--background)); padding: 4rem 0; }}
        .feature-card {{
            height: 100%; text-align: left; transition: var(--transition-smooth);
            background-color: hsl(var(--card)); border-radius: var(--radius);
            padding: 1.5rem; border: 1px solid hsl(var(--border));
        }}
        .feature-card:hover {{ transform: translateY(-5px); box-shadow: var(--shadow-lg); }}
        .feature-icon-wrapper {{
            width: 4rem; height: 4rem; border-radius: 1rem;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 1.5rem; font-size: 2rem;
            background: var(--gradient-primary); color: white;
        }}
        .feature-card h3 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.75rem; }}
        .feature-card p {{ color: hsl(var(--muted-foreground)); }}

        /* --- CTA Section --- */
        .cta-section {{
            background: var(--gradient-hero);
            padding: 5rem 1rem; margin-top: 3rem; text-align: center;
        }}
        .cta-section h2 {{
            font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 1.5rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        }}
        .cta-section p {{
            font-size: 1.1rem; color: rgba(255,255,255,0.95);
            margin-bottom: 2rem; max-width: 600px; margin: auto;
        }}
        #cta_signup_btn button {{
            background: var(--gradient-accent) !important; color: white !important;
            box-shadow: var(--shadow-glow) !important; padding: 0.75rem 3rem !important;
            font-size: 1.1rem !important; font-weight: 700 !important;
            border-radius: var(--radius) !important; border: none !important;
        }}

        /* --- Responsive --- */
        @media (max-width: 768px) {{
            .hero-content h1 {{ font-size: 2.5rem; }}
            .hero-content p {{ font-size: 1rem; }}
            .hero-buttons-container {{ flex-direction: column; }}
            .cta-section h2 {{ font-size: 2rem; }}
        }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        /* --- FIX: Make metric cards visible (with envelope look) --- */
        .metric-card {
            background: hsl(var(--card)) !important;
            border: 1px solid hsl(var(--border)) !important;
            border-radius: var(--radius) !important;
            box-shadow: var(--shadow-md) !important;
            padding: 2rem 1.5rem !important;
            text-align: center !important;
            transition: var(--transition-smooth) !important;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg) !important;
        }
        .metric-value {
            font-size: 2.25rem !important;
            font-weight: 800 !important;
            color: hsl(var(--foreground)) !important;
        }
        .metric-label {
            font-size: 0.9rem !important;
            color: hsl(var(--muted-foreground)) !important;
            font-weight: 600 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Checkbox visibility fix ---
    st.markdown("""
    <style>
        /* Checkbox text visibility */
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stCheckbox"] label span {
            color: #16182c !important;
            font-weight: 600;
        }

        /* Highlight selected checkbox */
        div[data-testid="stCheckbox"] input:checked + div,
        div[data-testid="stCheckbox"] [aria-checked="true"] {
            background-color: hsl(221, 83%, 90%) !important;
            border-radius: 6px !important;
            transition: all 0.2s ease-in-out;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        .stTextInput input,
        .stTextArea textarea {
            color: #16182c !important; /* Hardcoded dark gray for input fields */
        }
       
        /* --- THIS IS THE NEW, STRONGER RULE --- */
        /* This targets ANY text element inside the selectbox button */
        .stSelectbox div[role="button"] * {
             color: #16182c !important;
        }
       
        /* This targets any text inside the radio button label */
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span {
            color: #16182c !important;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    # --- END DEFINITIVE FIX ---


# --- DATABASE CONNECTION (MySQL) ---
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NiRvAn_*99',
            database='final_dcdsl_project' 
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        st.error(f"DB Connect Error: {err}")
        st.stop()
    return None

def query_db(query, params=None):
    conn = get_db_connection()
    if conn is None:
        st.error("DB Connection is None, cannot query.")
        return pd.DataFrame()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return pd.DataFrame(result)
    except mysql.connector.Error as err:
        st.error(f"DB Query Error: {err}")
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_db(query, params):
    conn = get_db_connection()
    if conn is None:
        st.error("DB Connection is None, cannot execute.")
        return False, None
    last_id = None
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        return True, last_id
    except mysql.connector.Error as err:
        st.error(f"DB Execute Error: {err}")
        try:
            conn.rollback()
        except:
            pass
        return False, None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# --- AUTHENTICATION FUNCTIONS ---


def authenticate_user(email, password, role):
    email_cleaned = email.replace(u'\xa0', '').strip()
    password_cleaned = password.replace(u'\xa0', '').strip()
    role_cleaned = role.strip()


    # Hash the CLEANED password
    password_hash = hash_password(password_cleaned)
   
    # Query using the CLEANED variables
    query = "SELECT * FROM USERS WHERE email = %s AND password_hash = %s AND role = %s"
    df = query_db(query, (email_cleaned, password_hash, role_cleaned))
   
    return df.iloc[0].to_dict() if not df.empty else None


def register_user(name, phone, email, password):
    if not all([name, phone, email, password]):
        return False


    # Clean all inputs
    name_cleaned = name.replace(u'\xa0', '').strip()
    phone_cleaned = phone.replace(u'\xa0', '').strip()
    email_cleaned = email.replace(u'\xa0', '').strip()
    password_cleaned = password.replace(u'\xa0', '').strip()


    # Check that cleaned inputs are still valid
    if not all([name_cleaned, phone_cleaned, email_cleaned, password_cleaned]):
        st.error("Fields cannot be blank or just spaces.")
        return False
   
    if len(password_cleaned) < 6:
        st.error("Password must be at least 6 characters.")
        return False


    password_hash = hash_password(password_cleaned)
    query = "INSERT INTO USERS (name, phone, email, role, password_hash) VALUES (%s, %s, %s, 'citizen', %s)"
    success, _ = execute_db(query, (name_cleaned, phone_cleaned, email_cleaned, password_hash))
    return success


# --- DATA RETRIEVAL FUNCTIONS ---


def get_statistics(user_id=None):
    stats = {'total': 0, 'Pending': 0, 'In-Progress': 0, 'Resolved': 0, 'Closed': 0, 'Duplicate': 0}
    if user_id:
        query, params = "SELECT s.status_name as status, COUNT(*) as count FROM ISSUES i JOIN STATUS s ON i.status_id = s.status_id WHERE i.user_id = %s GROUP BY s.status_name", (user_id,)
        total_q, total_p = "SELECT COUNT(*) as total FROM ISSUES WHERE user_id = %s", (user_id,)
    else:
        query, params = "SELECT s.status_name as status, COUNT(*) as count FROM ISSUES i JOIN STATUS s ON i.status_id = s.status_id GROUP BY s.status_name", None
        total_q, total_p = "SELECT COUNT(*) as total FROM ISSUES", None


    stats_df = query_db(query, params)
    total_df = query_db(total_q, total_p)
    total = total_df['total'].iloc[0] if not total_df.empty else 0
    stats['total'] = total


    if not stats_df.empty:
        for _, row in stats_df.iterrows():
            if row['status'] in stats:
                stats[row['status']] = row['count']
    return stats


@st.cache_data(ttl=600)
def get_issues_by_category():
    return query_db("SELECT c.Name as category, COUNT(i.issue_id) as count FROM CATEGORIES c LEFT JOIN ISSUES i ON c.category_id = i.category_id GROUP BY c.Name ORDER BY count DESC")


@st.cache_data(ttl=600)
def get_issues_timeline():
    return query_db("SELECT DATE(created_at) as date, s.status_name as status, COUNT(*) as count FROM ISSUES i JOIN STATUS s ON i.status_id = s.status_id WHERE created_at >= CURDATE() - INTERVAL 30 DAY GROUP BY DATE(created_at), s.status_name ORDER BY date")


@st.cache_data(ttl=600)
def get_issues_by_area():
    return query_db("SELECT l.area, COUNT(i.issue_id) as count FROM LOCATIONS l JOIN ISSUES i ON l.location_id = i.location_id GROUP BY l.area ORDER BY count DESC LIMIT 10")


@st.cache_data(ttl=3600)
def get_all_locations():
    return query_db("SELECT location_id, area, address, latitude, longitude FROM LOCATIONS ORDER BY area")


@st.cache_data(ttl=3600)
def get_all_categories():
    return query_db("SELECT category_id, Name FROM CATEGORIES ORDER BY Name")


@st.cache_data(ttl=3600)
def get_all_status():
    return query_db("SELECT status_id, status_name FROM STATUS")


@st.cache_data(ttl=30)
def get_user_issues(user_id):
    query = "SELECT i.issue_id, c.Name as category, i.description, l.area, i.severity, s.status_name as status, i.created_at FROM ISSUES i JOIN CATEGORIES c ON i.category_id = c.category_id JOIN LOCATIONS l ON i.location_id = l.location_id JOIN STATUS s ON i.status_id = s.status_id WHERE i.user_id = %s ORDER BY i.created_at DESC"
    return query_db(query, (user_id,))


@st.cache_data(ttl=30)
def get_all_issues_detailed():
    # This query uses a Window Function to find the *last* person
    # who changed each issue, based on your history table.
    query = """
    WITH LatestHistory AS (
        SELECT
            rh.issue_id,
            rh.changed_by,
            u_updater.name as updated_by_name,
            -- Use ROW_NUMBER to find the single latest entry per issue
            ROW_NUMBER() OVER(PARTITION BY rh.issue_id ORDER BY rh.timestamp DESC) as rn
        FROM resolution_history rh
        LEFT JOIN USERS u_updater ON rh.changed_by = u_updater.user_id
    )
    SELECT
        i.issue_id,
        u.name as reporter,
        lh.updated_by_name as updated_by, -- This is the staff updater's name
        c.Name as category,
        i.description,
        l.area,
        l.address,
        l.latitude,  -- <-- From locations table 'l'
        l.longitude, -- <-- From locations table 'l'
        i.severity,
        s.status_name as status,
        i.created_at,
        i.updated_at,
        i.photo_path
    FROM ISSUES i
    LEFT JOIN USERS u ON i.user_id = u.user_id
    LEFT JOIN CATEGORIES c ON i.category_id = c.category_id
    LEFT JOIN LOCATIONS l ON i.location_id = l.location_id
    LEFT JOIN STATUS s ON i.status_id = s.status_id
    -- Join with LatestHistory, but only take the latest one (rn = 1)
    LEFT JOIN LatestHistory lh ON i.issue_id = lh.issue_id AND lh.rn = 1
    ORDER BY i.issue_id ASC
    """
    return query_db(query)


@st.cache_data(ttl=30)
def get_issue_history(issue_id):
    query = """
    SELECT
        rh.timestamp,
        u.name as updater_name,
        s_old.status_name as old_status,
        s_new.status_name as new_status
    FROM resolution_history rh
    JOIN USERS u ON rh.changed_by = u.user_id
    JOIN STATUS s_old ON rh.old_status_id = s_old.status_id
    JOIN STATUS s_new ON rh.new_status_id = s_new.status_id
    WHERE rh.issue_id = %s
    ORDER BY rh.timestamp DESC
    """
    return query_db(query, (issue_id,))


def submit_issue(user_id, category_id, location_id, description, severity, photo_path=None):
    query = """
    INSERT INTO ISSUES
    (user_id, category_id, location_id, status_id, description, severity, photo_path, created_at, updated_at, master_issue_id)
    VALUES (%s, %s, %s, 1, %s, %s, %s, NOW(), NOW(), NULL)
    """
    success, last_id = execute_db(query, (user_id, category_id, location_id, description, severity, photo_path))
    return success, last_id


def update_issue_status(issue_id, new_status_id, staff_user_id):
    # This prevents the "numpy.int64 cannot be converted" error.
    try:
        py_issue_id = int(issue_id)
        py_new_status_id = int(new_status_id)
        py_staff_user_id = int(staff_user_id)
    except ValueError as e:
        st.error(f"Invalid ID provided: {e}")
        return False


    # 1. Get the old status_id first
    # We use the Python-native int (py_issue_id) in the query
    old_status_df = query_db("SELECT status_id FROM ISSUES WHERE issue_id = %s", (py_issue_id,))
    if old_status_df.empty:
        st.error("Issue not found.")
        return False
   
    py_old_status_id = int(old_status_df['status_id'].iloc[0])


    # 2. Check if status is actually changing
    if py_old_status_id == py_new_status_id:
        return True # Nothing to do


    # 3. Use a NEW, SEPARATE connection for the transaction
    conn = None
    cursor = None
    try:
        # Create a fresh connection just for this transaction
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NiRvAn_*99',
            database='final_dcdsl_project' 
        )
        if not conn.is_connected():
            st.error("Database connection failed for transaction.")
            return False


        cursor = conn.cursor()
       
        # First, update the main issue table
        # We use the Python-native int variables here
        query_update = "UPDATE ISSUES SET status_id = %s, updated_at = NOW() WHERE issue_id = %s"
        cursor.execute(query_update, (py_new_status_id, py_issue_id))
       
        # Second, insert into the history table
        query_log = """
        INSERT INTO resolution_history
        (issue_id, old_status_id, new_status_id, changed_by, timestamp)
        VALUES (%s, %s, %s, %s, NOW())
        """
        # We use the Python-native int variables here
        cursor.execute(query_log, (py_issue_id, py_old_status_id, py_new_status_id, py_staff_user_id))
       
        # If both are successful, commit
        conn.commit()
        return True
       
    except mysql.connector.Error as err:
        st.error(f"DB Transaction Error: {err}")
        if conn:
            try:
                conn.rollback() # Rollback changes on error
            except:
                pass
        return False
    finally:
        # Clean up the cursor and the NEW connection
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# --- PLOTTING FUNCTIONS ---


def create_status_chart(stats):
    labels = ['Pending', 'In-Progress', 'Resolved', 'Closed', 'Duplicate']
    values = [stats['Pending'], stats['In-Progress'], stats['Resolved'], stats['Closed'], stats['Duplicate']]
    colors = ['hsl(28, 100%, 53%)', 'hsl(221, 83%, 53%)', 'hsl(142, 71%, 45%)', 'hsl(215, 16%, 47%)', 'hsl(0, 84%, 60%)']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, marker=dict(colors=colors, line=dict(color='#ffffff', width=2)), textinfo='percent', textfont=dict(size=14, color='white'), hovertemplate='<b>%{label}</b><br>Count: %{value}<br>(%{percent})<extra></extra>')])
    fig.update_layout(showlegend=True, height=350, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', size=12, color='hsl(222, 47%, 11%)'), title=dict(text='Status Distribution', font=dict(size=18)), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    return fig


def create_category_chart(df):
    fig = px.bar(df.sort_values('count', ascending=True), x='count', y='category', orientation='h', text='count', color='count', color_continuous_scale=px.colors.sequential.Blues)
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', size=12, color='hsl(222, 47%, 11%)'), title=dict(text='Issues by Category', font=dict(size=18)), xaxis=dict(title='Number of Issues', gridcolor='hsl(214, 32%, 91%)'), yaxis=dict(title='', gridcolor='rgba(0,0,0,0)'), margin=dict(l=20, r=20, t=60, b=20))
    return fig


def create_timeline_chart(df):
    color_map = {
        'Pending': 'hsl(28, 100%, 53%)',
        'In-Progress': 'hsl(221, 83%, 53%)',
        'Resolved': 'hsl(142, 71%, 45%)',
        'Closed': 'hsl(215, 16%, 47%)',
        'Duplicate': 'hsl(0, 84%, 60%)'
    }
    fig = px.bar(df, x='date', y='count', color='status', color_discrete_map=color_map, title='Issues Over Time (Last 30 Days)')
    fig.update_layout(height=400, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', size=12, color='hsl(222, 47%, 11%)'), title=dict(text='Issues Timeline (Last 30 Days)', font=dict(size=18)), xaxis=dict(title='Date', gridcolor='hsl(214, 32%, 91%)'), yaxis=dict(title='Count', gridcolor='hsl(214, 32%, 91%)'), legend=dict(title='Status', orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), margin=dict(l=20, r=20, t=60, b=80))
    return fig


def create_area_chart(df):
    fig = px.bar(df.sort_values('count', ascending=False), x='area', y='count', text='count', color='count', color_continuous_scale=px.colors.sequential.Greens)
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', size=12, color='hsl(222, 47%, 11%)'), title=dict(text='Top 10 Areas by Issue Count', font=dict(size=18)), xaxis=dict(title='Area', gridcolor='rgba(0,0,0,0)'), yaxis=dict(title='Issues', gridcolor='hsl(214, 32%, 91%)'), margin=dict(l=20, r=20, t=60, b=20))
    return fig

# --- SESSION STATE INITIALIZATION ---

def init_session_state():
    defaults = {'logged_in': False, 'user_id': None, 'user_name': None, 'user_role': None, 'current_page': 'home', 'locations_df': pd.DataFrame(), 'categories_df': pd.DataFrame(), 'status_df': pd.DataFrame()}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    if st.session_state.locations_df.empty:
        st.session_state.locations_df = get_all_locations()
    if st.session_state.categories_df.empty:
        st.session_state.categories_df = get_all_categories()
    if st.session_state.status_df.empty:
        st.session_state.status_df = get_all_status()

# --- UI PAGES ---

def home_page():
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>PMC Civic Issue<br><span style="color: #f0f0f0; opacity: 0.9;">Management Portal</span></h1>
            <p>Making our city better, one report at a time. Report civic issues and track their resolution seamlessly.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown('<div class="container" style="margin-top: -5rem; position: relative; z-index: 3;">', unsafe_allow_html=True)
    cols_hero_btns = st.columns([1, 1.2, 1.2, 1])
    with cols_hero_btns[1]:
        st.markdown('<div id="hero_start">', unsafe_allow_html=True)
        if st.button("Get Started", use_container_width=True, key="home_get_started"):
            st.session_state.current_page = 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with cols_hero_btns[2]:
        st.markdown('<div id="hero_dash">', unsafe_allow_html=True)
        if st.button("View Dashboard", use_container_width=True, key="home_view_dash"):
            st.session_state.current_page = 'dashboard' if st.session_state.logged_in else 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    # --- DYNAMIC STATS ---
    stats_dict = get_statistics()
    active_issues = stats_dict.get('Pending', 0) + stats_dict.get('In-Progress', 0)
    resolved_issues = stats_dict.get('Resolved', 0) + stats_dict.get('Closed', 0)


    # --- DYNAMIC AVG RESOLUTION CALCULATION (FIXED) ---
    # This query uses resolution_history for 100% accuracy
    avg_res_str = "N/A"
   
    # We use status_id 3 (Resolved) and 4 (Closed)
    avg_query = """
    WITH ResolutionTime AS (
        SELECT
            i.issue_id,
            i.created_at,
            MIN(rh.timestamp) as resolution_timestamp
        FROM ISSUES i
        JOIN resolution_history rh ON i.issue_id = rh.issue_id
        WHERE rh.new_status_id IN (3, 4) -- 3: Resolved, 4: Closed
        GROUP BY i.issue_id, i.created_at
    )
    SELECT
        AVG(TIMESTAMPDIFF(DAY, created_at, resolution_timestamp)) as avg_days,
        AVG(TIMESTAMPDIFF(HOUR, created_at, resolution_timestamp)) as avg_hours
    FROM ResolutionTime
    """
    avg_res_df = query_db(avg_query)


    if not avg_res_df.empty and avg_res_df['avg_days'].iloc[0] is not None:
        avg_days = avg_res_df['avg_days'].iloc[0]
        avg_hours = avg_res_df['avg_hours'].iloc[0]


        if avg_days is not None:
            if avg_days < 1.0 and avg_hours is not None:
                avg_res_str = f"{avg_hours:.1f} hours"
            else:
                avg_res_str = f"{avg_days:.1f} days"
    # --- END DYNAMIC AVG RESOLUTION ---


    # Citizens Count
    total_citizens = 0
    citizens_df = query_db("SELECT COUNT(*) as count FROM USERS WHERE role = 'citizen'")
    if not citizens_df.empty:
        total_citizens = citizens_df['count'].iloc[0]


    active_issues_str = f"{active_issues:,}"
    resolved_issues_str = f"{resolved_issues:,}"
    total_citizens_str = f"{total_citizens:,}"
    # --- END DYNAMIC STATS ---


    st.markdown("<div class='stats-section'><div class='container'>", unsafe_allow_html=True)


    stats_data = [
        {"icon": "⏳", "label": "Active Issues", "value": active_issues_str, "color": "text-warning", "bgColor": "bg-warning-light"},
        {"icon": "✅", "label": "Resolved", "value": resolved_issues_str, "color": "text-success", "bgColor": "bg-success-light"},
        {"icon": "⏱", "label": "Avg Resolution", "value": avg_res_str, "color": "text-primary", "bgColor": "bg-accent-light"},
        {"icon": "👥", "label": "Citizens", "value": total_citizens_str, "color": "text-accent", "bgColor": "bg-accent-light"}
    ]


    cols = st.columns(4)
    for i, stat in enumerate(stats_data):
        with cols[i]:
            st.markdown(f"""
            <div class='card shadow-md metric-card transition-smooth'>
                <div class='metric-icon-wrapper {stat['bgColor']}'>
                    <span class='{stat['color']}'>{stat['icon']}</span>
                </div>
                <p class='metric-value'>{stat['value']}</p>
                <p class='metric-label'>{stat['label']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


    st.markdown("<div class='features-section'><div class='container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 2.5rem; font-weight: 700; margin-bottom: 3rem;'>How It Works</h2>", unsafe_allow_html=True)
    features_data = [
        {"title": "Report Issues", "description": "Quickly report civic issues like potholes, garbage, or broken streetlights in your area.", "icon": "📢"},
        {"title": "Track Progress", "description": "Monitor the status of your reported issues in real-time with detailed updates.", "icon": "🔄"},
        {"title": "Location-Based", "description": "View issues on an interactive map and find problems near you instantly.", "icon": "🗺"}
    ]
    cols = st.columns(3)
    for i, feature in enumerate(features_data):
        with cols[i]:
            st.markdown(f"""
            <div class='card shadow-md feature-card transition-smooth'>
                <div class='feature-icon-wrapper'>
                    <span>{feature['icon']}</span>
                </div>
                <h3>{feature['title']}</h3>
                <p>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


    # --- CTA Section ---
    st.markdown("""
    <div class='cta-section'>
        <div class='container' style='text-align: center;'>
            <h2 style='font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 1.5rem; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);'>Ready to Make a Difference?</h2>
            <p style='font-size: 1.1rem; color: rgba(255, 255, 255, 0.95); margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.15);'>Join thousands of citizens working together to improve our city's infrastructure and quality of life.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    cols_cta = st.columns([1, 1, 1])
    with cols_cta[1]:
        st.markdown('<div id="cta_signup_btn">', unsafe_allow_html=True)
        if st.button("Sign Up Now ", use_container_width=True, key="cta_signup_final"):
            st.session_state.current_page = 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


    st.markdown("<footer class='footer'><p>© 2025 Pune Municipal Corporation. All rights reserved.</p></footer>", unsafe_allow_html=True)




def auth_page():
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)


    st.markdown("<div class='container' style='padding-top: 1rem;'>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        st.session_state.current_page = 'home'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


    # --- Main Auth Card ---
    st.markdown(f"<div class='auth-card card shadow-elegant'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 1.75rem; margin-bottom: 0.5rem;'>PMC Civic Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: hsl(var(--muted-foreground)); margin-bottom: 1.5rem;'>Sign in or create an account</p>", unsafe_allow_html=True)
   
    # Separate the Login and Signup flows using tabs
    login_tab, signup_tab = st.tabs(["🔒 Sign In", "📝 Sign Up (Citizen Only)"])
   
    # 2. LOGIN SECTION
    with login_tab:
       
        # --- IMPLEMENTING REQUEST 1: Clear Login Sections via Radio Button ---
        st.markdown("<h4 style='text-align:center; margin-bottom:0.5rem; font-size: 1.1rem; font-weight: 600;'>Select Login Role</h4>", unsafe_allow_html=True)
       
        # THIS IS THE COMPONENT FOR THE TWO SECTIONS
        role = st.radio(
            "Login As",
            ["Citizen", "Staff"],
            horizontal=True,
            index=0,
            key="login_role_radio_final",
            label_visibility="collapsed"
        )
       
        # --- Login Form ---
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
           
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        # The .lower() converts "Citizen" or "Staff" to the required 'citizen' or 'staff' for the database.
                        user_role_to_check = role.lower()
                        user = authenticate_user(email, password, user_role_to_check)


                        if user:
                            # --- CLEAR CACHE ON LOGIN ---
                            st.cache_data.clear()
                            # ---------------------------


                            st.session_state.logged_in = True
                            st.session_state.user_id = user['user_id']
                            st.session_state.user_name = user['name']
                            st.session_state.user_role = user['role']
           
                            # Redirect upon successful login
                            st.success(f"Welcome, {user['name']}!")
                            time.sleep(1)
                            st.session_state.current_page = 'dashboard'
                            st.rerun()
                        else:
                            st.error(f"Invalid credentials. Check email, password, and ensure you selected *{role}*.")


    # --- Sign Up Tab (Citizen Only) ---
    with signup_tab:
        # Prevent staff from signing up
        st.info("Sign Up is only for new Citizens. Staff accounts are created by an administrator.")


        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Ravi Sharma", key="signup_name")
            phone = st.text_input("Phone Number", placeholder="9876543210", key="signup_phone")
            email = st.text_input("Email", placeholder="ravi.sharma@gmail.com", key="signup_email")
            password = st.text_input("Create Password", type="password", placeholder="Min. 6 characters", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Create Citizen Account", use_container_width=True, type="primary")
           
            if submit:
                if not all([name, phone, email, password, confirm_password]):
                    st.error("Please fill out all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        success = register_user(name, phone, email, password)
               
                        if success:
                            st.success("Account created! Please switch to the Sign In tab and log in as a Citizen.")
                            time.sleep(2)
                            st.session_state.current_page = 'auth'
                            st.rerun()
                        else:
                            st.error("Account creation failed (email/phone likely exists).")
                           
    st.markdown("</div>", unsafe_allow_html=True)


    # --- DEMO CREDENTIALS ---
    with st.expander("Demo Credentials"):
        st.code("Citizen Email: ravi.sharma@gmail.com | Pass: Ravi@123")
        st.code("Staff Email:   santosh.rao@pmc.gov.in | Pass: Santosh@123")




def dashboard_page():
    st.markdown("<style>[data-testid='stSidebar'] {display: block;}</style><div class='container' style='padding-top: 1rem;'>", unsafe_allow_html=True)
    if st.session_state.user_role == 'citizen':
        citizen_dashboard()
    else:
        staff_dashboard()
    st.markdown("</div>", unsafe_allow_html=True)


def citizen_dashboard():
    st.markdown(f"<div class='dashboard-header'><h1>PMC Civic Portal</h1><p>Welcome back, {st.session_state.user_name}</p></div>", unsafe_allow_html=True)
   
    if st.button("➕ Report New Issue", use_container_width=True, type="primary"):
        st.session_state.current_page = 'submit_issue'
        st.rerun()
   
    st.markdown("<br>", unsafe_allow_html=True)
   
    stats = get_statistics(st.session_state.user_id)
    cols = st.columns(4)
    stat_items = [
        {"label": "Pending", "value": stats['Pending'], "icon": "⏳", "color": "text-warning", "bgColor": "bg-warning-light"},
        {"label": "In Progress", "value": stats['In-Progress'], "icon": "🔄", "color": "text-primary", "bgColor": "bg-accent-light"},
        {"label": "Resolved", "value": stats['Resolved'] + stats['Closed'], "icon": "✅", "color": "text-success", "bgColor": "bg-success-light"},
        {"label": "Total Reports", "value": stats['total'], "icon": "📊", "color": "text-primary", "bgColor": "bg-accent-light"}
    ]
   
    for i, item in enumerate(stat_items):
        with cols[i]:
            st.markdown(f"<div class='card metric-card shadow-md transition-smooth'><div class='metric-icon-wrapper {item['bgColor']}'><span class='{item['color']}'>{item['icon']}</span></div><p class='metric-value'>{item['value']}</p><p class='metric-label'>{item['label']}</p></div>", unsafe_allow_html=True)
   
    st.markdown("---")
    st.markdown("<h2 style='font-size: 1.75rem; font-weight: 700;'>Recent Issues</h2>", unsafe_allow_html=True)
   
    issues_df = get_user_issues(st.session_state.user_id)
   
    if not issues_df.empty:
        for _, issue in issues_df.iterrows():
            status_class = f"status-{str(issue['status']).lower().replace(' ', '-')}"
            with st.expander(f"#{issue['issue_id']} • {issue['category']} in {issue['area']}"):
                st.markdown(f"*Desc:* {issue['description']} | *Severity:* {issue['severity']} | *Reported:* {issue['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"*Status:* <span class='status-badge {status_class}'>{issue['status']}</span>", unsafe_allow_html=True)
    else:
        st.info("No issues reported yet.")


def staff_dashboard():
    st.markdown(f"<div class='dashboard-header'><h1>Staff Dashboard</h1><p>Welcome, {st.session_state.user_name}</p></div>", unsafe_allow_html=True)
   
    stats = get_statistics()
    cols = st.columns(5)
    cols[0].metric("Total", stats['total'])
    cols[1].metric("Pending", stats['Pending'])
    cols[2].metric("In Progress", stats['In-Progress'])
    cols[3].metric("Resolved", stats['Resolved'])
    cols[4].metric("Closed", stats['Closed'])
   
    st.markdown("<br>", unsafe_allow_html=True)
   
    tab_manage, tab_analytics = st.tabs(["📋 Issue Management", "📊 Analytics"])
   
    with tab_manage:
        st.subheader("Manage Issues")
        all_issues = get_all_issues_detailed()
        status_df = st.session_state.status_df
        status_map = {row['status_name']: row['status_id'] for _, row in status_df.iterrows()}
        status_list = list(status_map.keys())
       
        if all_issues.empty:
            st.info("No issues found.")
            # We add a 'return' here to prevent the code below from running on an empty DF
            return
       
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter Status", ["All"] + status_list, key="f_status")
        with col2:
            severity_filter = st.selectbox("Filter Severity", ["All", "High", "Medium", "Low"], key="f_sev")
        with col3:
            category_filter = st.selectbox("Filter Category", ["All"] + list(st.session_state.categories_df['Name'].unique()), key="f_cat")
       
        filtered_df = all_issues.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        if severity_filter != "All":
            filtered_df = filtered_df[filtered_df['severity'] == severity_filter]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df['category'] == category_filter]
       
        st.caption(f"Showing {len(filtered_df)} issues")
       
        if filtered_df.empty:
            st.info("No issues found for the selected filters.")
        else:
            for _, issue in filtered_df.iterrows():
                status_class = f"status-{str(issue['status']).lower().replace(' ', '-')}"
                with st.expander(f"#{issue['issue_id']} • {issue['category']} ({issue['severity']}) - {issue['area']}"):
                   
                    # Check if the 'updated_by' column exists and is not null
                    if 'updated_by' in issue and pd.notna(issue['updated_by']):
                        updater_name = issue['updated_by']
                    else:
                        updater_name = "N/A" # No update history yet
                       
                    st.markdown(f"**Description:** {issue['description']}  \n**Reporter:** {issue['reporter']} | **Last Update By:** {updater_name} | **Address:** {issue['address']}")
                    st.markdown(f"**Reported:** {issue['created_at'].strftime('%Y-%m-%d %H:%M')} | **Status:** <span class='status-badge {status_class}'>{issue['status']}</span>", unsafe_allow_html=True)
                   
                    if 'photo_path' in issue and pd.notna(issue['photo_path']):
                        st.caption(f"Photo: {issue['photo_path']}")
                   
                    # --- NEW: VISUAL UI FOR HISTORY ---
                    with st.expander("Show Update History"):
                        history_df = get_issue_history(issue['issue_id'])
                        if history_df.empty:
                            st.write("No update history for this issue yet.")
                        else:
                            for _, row in history_df.iterrows():
                                # Format timestamp to a readable string
                                ts = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                                st.markdown(f"**{ts}**: **{row['updater_name']}** changed status from *{row['old_status']}* to **{row['new_status']}**.")
                    # --- END NEW UI ---
                   
                    st.markdown("---")
                    col_upd, col_btn = st.columns([2, 1])
                    with col_upd:
                        current_status_index = 0
                        if issue['status'] in status_list:
                            current_status_index = status_list.index(issue['status'])
                       
                        new_stat_name = st.selectbox("Set Status", status_list, index=current_status_index, key=f"sel_{issue['issue_id']}")
                    with col_btn:
                        st.markdown("<div style='height: 2.4rem;'></div>", unsafe_allow_html=True)
                        if st.button("Update", key=f"btn_{issue['issue_id']}", use_container_width=True):
                            new_stat_id = status_map[new_stat_name]
                           
                            # Pass the logged-in staff member's ID
                            if update_issue_status(issue['issue_id'], new_stat_id, st.session_state.user_id):
                                st.success(f"Issue #{issue['issue_id']} updated and logged!")
                                st.cache_data.clear() # Clear cache to refresh data
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Update failed. Check DB logs.")
                           
    with tab_analytics:
        st.subheader("Analytics Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_status_chart(stats), use_container_width=True)
            st.plotly_chart(create_area_chart(get_issues_by_area()), use_container_width=True)
        with col2:
            st.plotly_chart(create_category_chart(get_issues_by_category()), use_container_width=True)
            st.plotly_chart(create_timeline_chart(get_issues_timeline()), use_container_width=True)


def submit_issue_page():
    st.markdown("<style>[data-testid='stSidebar'] {display: block;}</style><div class='container' style='padding-top: 1rem;'>", unsafe_allow_html=True)
    st.title("Report New Issue")
    st.markdown("Fill in the details below.")
    st.markdown("---")
   
    locations, categories = st.session_state.locations_df, st.session_state.categories_df
    if locations.empty or categories.empty:
        st.error("Failed to load data.")
        return
   
    location_map = {f"{row['area']} ({row['address']})": row['location_id'] for _, row in locations.iterrows()}
    category_map = {row['Name']: row['category_id'] for _, row in categories.iterrows()}
   
    uploaded_file = st.file_uploader("Upload Photo (Optional)", type=["jpg", "jpeg", "png"])
           
    st.markdown("<div class='card shadow-md' style='max-width: 700px; margin: 1rem auto;'>", unsafe_allow_html=True)
    with st.form("submit_form"):
        st.subheader("Issue Details")
       
        category_name = st.selectbox("Category *", category_map.keys())
       
        loc_keys = list(location_map.keys())
        location_key = st.selectbox("Location *", loc_keys, index=0)
       
        description = st.text_area("Description *", height=150, placeholder="Provide details...")
        severity = st.selectbox("Severity *", ["Low", "Medium", "High"])
        st.markdown("<br>", unsafe_allow_html=True)
       
        submitted = st.form_submit_button("Submit Issue", use_container_width=True, type="primary")
       
        if submitted:
            if not all([description, location_key, category_name]):
                st.error("Please fill required fields")
            else:
                with st.spinner("Submitting..."):
                    loc_id, cat_id = location_map[location_key], category_map[category_name]
                    photo_path = f"/uploads/{uploaded_file.name}" if uploaded_file else None  # Placeholder
                    success, issue_id = submit_issue(st.session_state.user_id, cat_id, loc_id, description, severity, photo_path)
                   
                    if success:
                        st.success(f"Issue #{issue_id} submitted!")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.session_state.current_page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Submission failed.")
                       
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- MAIN ROUTER ---


def main():
   
    # Loads all custom CSS, including the fix for invisible text and radio buttons
    load_react_ui_css()
   
    # Initialize session variables and load cached data (locations, categories)
    init_session_state()


    # Sidebar Navigation (only shows if logged in)
    if st.session_state.logged_in:
        with st.sidebar:
            st.markdown(f"<h1 style='color: white; text-align: center; font-size: 1.5rem; margin-top: 1rem;'>🏛 PMC Portal</h1><hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
            st.success(f"Logged in:\n*{st.session_state.user_name}*")
            st.caption(f"Role: {st.session_state.user_role.capitalize()}")
            st.markdown("<br>", unsafe_allow_html=True)
           
            if st.button("Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
            if st.session_state.user_role == 'citizen':
                if st.button("Report Issue", use_container_width=True):
                    st.session_state.current_page = 'submit_issue'
                    st.rerun()
           
            # --- "Live Map" button REMOVED ---
           
            st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'><br>", unsafe_allow_html=True)
           
            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key != 'current_page': # Keep current_page to stay on 'home'
                         del st.session_state[key]
               
                # Reset to default state
                init_session_state()
                st.session_state.logged_in = False
                st.session_state.current_page = 'home'
               
                st.cache_data.clear()
                st.rerun()


    # Page Routing
    pages = {'home': home_page, 'auth': auth_page, 'dashboard': dashboard_page, 'submit_issue': submit_issue_page}
    page_function = pages.get(st.session_state.get('current_page', 'home'), home_page)
    page_function()


if __name__ == "__main__":
    main()
