import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import os
import re
from datetime import datetime, date, timedelta
from pathlib import Path

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Satellite Monitoring Dashboard"

# === CONFIGURATION FOR DASHBOARD 1 (Satellite Attitude) ===
BASE_DIR_SAT = "satellite data"
SATELLITES = ["3R Data", "3SR Data"]
FILE_PREFIX = {
    "3R Data": "3RIMG",
    "3SR Data": "3SIMG"
}
column_names = ['year', 'month', 'day', 'hour', 'minute', 'second', 
                'millisecond', 'scan_value', 'yaw', 'pitch', 'roll']

# === CONFIGURATION FOR DASHBOARD 2 (File Monitoring) ===
LOG_FILE_PATH = "LOGS/gfs.log"
TIME_INTERVALS = ["00", "06", "12", "18"]
SEQUENCES = [f"F{str(i).zfill(2)}" for i in range(0, 25, 3)]

# === Constants for Dashboard 3 (FAX/OD) ===
BASE_DIR_OD = "LOGS/FAX"
LOG_FILES_FAX = {
    "INS3RR": os.path.join(BASE_DIR_OD, "fax_updation_ins3rr.log"),
    "INS3RM": os.path.join(BASE_DIR_OD, "fax_updation_ins3rm.log"),
    "INS3SR": os.path.join(BASE_DIR_OD, "fax_updation_ins3sr.log"),
    "INS3SM": os.path.join(BASE_DIR_OD, "fax_updation_ins3sm.log"),
    "3DR": os.path.join(BASE_DIR_OD, "fax_reception_3r.log"),
    "3DS": os.path.join(BASE_DIR_OD, "fax_reception_3s.log")
}
FILE_TYPE_MAPPING = {
    "INS3RR": "3R", "INS3RM": "3R", "INS3SR": "3S", "INS3SM": "3S", "3DR": "3D", "3DS": "3DS"
}

# === Constants for Dashboard 4 (OBT) ===
BASE_DIR_OBT = "LOGS/OBT"
LOG_FILES_OBT = {
    'INS3RM': f'{BASE_DIR_OBT}/obt_updation_ins3rm.log',
    'INS3RR': f'{BASE_DIR_OBT}/obt_updation_ins3rr.log',
    'INS3SM': f'{BASE_DIR_OBT}/obt_updation_ins3sm.log',
    'INS3SR': f'{BASE_DIR_OBT}/obt_updation_ins3sr.log',
    '3DR': f'{BASE_DIR_OBT}/obt_reception_3r.log',
    '3DS': f'{BASE_DIR_OBT}/obt_reception_3s.log'
}

# === HELPER FUNCTIONS FOR DASHBOARD 1 ===
def read_gpd_utc_dat(file_path):
    df = pd.read_csv(file_path, comment='#', engine='python',
                     names=column_names, sep='\s+')
    return df

def get_datetime_from_filename(filename):
    try:
        dt_str = filename.split("_")[1] + filename.split("_")[2]
        return datetime.strptime(dt_str, "%d%b%Y%H%M")
    except Exception:
        return None

def get_available_files(sat):
    folder_path = os.path.join(BASE_DIR_SAT, sat)
    if not os.path.exists(folder_path):
        return []
    files = [f for f in os.listdir(folder_path) if f.endswith(".dat.GPD_utc")]
    files_with_dt = [(get_datetime_from_filename(f), f) for f in files]
    return sorted([(dt, os.path.join(folder_path, f)) for dt, f in files_with_dt if dt])

def get_latest_file(sat):
    files = get_available_files(sat)
    return files[-1][1] if files else None

def get_time_options(sat, selected_date):
    folder_path = os.path.join(BASE_DIR_SAT, sat)
    try:
        if not os.path.exists(folder_path):
            return []
        files = os.listdir(folder_path)
        date_str = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d%b%Y").upper()
        matching_files = [f for f in files if date_str in f]
        options = []
        for f in matching_files:
            time_part = f.split("_")[2]
            if time_part.isdigit() and len(time_part) == 4:
                time_str = f"{time_part[:2]}:{time_part[2:]}"
                options.append({"label": time_str, "value": time_part})
        return sorted(options, key=lambda x: x['value'])
    except Exception:
        return []

# === HELPER FUNCTIONS FOR DASHBOARD 2 ===
def load_log_file():
    if not os.path.exists(LOG_FILE_PATH):
        return set()
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"Error reading log file: {e}")
        return set()

def check_file_availability(date_obj, utc, available_set):
    date_str = date_obj.strftime('%Y%m%d')
    return [(seq, f"{date_str}{utc}00_{seq}" in available_set) for seq in SEQUENCES]

def get_box_color_dashboard2(availability):
    return 'green' if availability else 'red'

def generate_file_boxes(availability_list):
    return [
        html.Div(
            seq,
            style={
                'display': 'inline-block',
                'margin': '5px 15px',
                'padding': '5px 8px',
                'border': '1px solid black',
                'backgroundColor': get_box_color_dashboard2(available),
                'color': 'black',
                'borderRadius': '3px',
                'width': '55px',
                'textAlign': 'center',
                'fontSize': '12px'
            }
        ) for seq, available in availability_list
    ]

# === Helper Functions for FAX Dashboard ===
def read_log_file_fax(log_file_path):
    try:
        if not os.path.exists(log_file_path):
            return []
        with open(log_file_path, 'r') as file:
            content = file.read()
        pattern = r'((?:3[DRS]|3R|3S|3DS)-\d{8}\d+\.txt(?:\.done)?)'
        filenames = re.findall(pattern, content)
        return filenames
    except Exception as e:
        print(f"Error reading {log_file_path}: {e}")
        return []

def get_matching_filename_fax(selected_date, log_type):
    log_file = LOG_FILES_FAX.get(log_type)
    if not log_file:
        return ""
    filenames = read_log_file_fax(log_file)
    
    # CHANGE 1: Remove the additional 2-day offset since the date picker will now show the correct date
    expected_file_date = selected_date.strftime('%Y%m%d')

    valid_prefixes = {
        "3DR": ["3DR", "3R"],
        "3DS": ["3DS", "3S"],
    }

    primary_prefix = FILE_TYPE_MAPPING.get(log_type, '3R')
    possible_prefixes = valid_prefixes.get(log_type, [primary_prefix])

    for filename in filenames:
        for prefix in possible_prefixes:
            if filename.startswith(f"{prefix}-{expected_file_date}"):
                return filename

    return "Not Found"

# === Helper Functions for OBT Dashboard 4 ===
def parse_date_from_log(date_str):
    try:
        return datetime.strptime(date_str, '%d%b%Y').date()
    except Exception:
        return None

def read_log_file_obt(log_file_path):
    try:
        if not os.path.exists(log_file_path):
            return []
        matched_lines = []
        with open(log_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    matched_lines.append(line)
        return matched_lines
    except Exception as e:
        print(f"Error reading {log_file_path}: {e}")
        return []

def get_matching_filename_obt(selected_date, log_type):
    lines = read_log_file_obt(LOG_FILES_OBT[log_type])
    expected_date = selected_date.strftime('%d%b%Y').upper()
    for line in lines:
        if expected_date in line:
            return line.split()[0] if log_type.startswith('INS') else line
    return "Not Found"


# === Style Functions for dashboard 3 AND 4 only===
def base_style_small():
    return {
        'width': '80px', 'height': '40px', 'borderRadius': '6px', 
        'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 
        'margin': '3px', 'fontSize': '10px'
    }

def base_style_large():
    return {
        'width': '100px', 'height': '50px', 'borderRadius': '6px', 
        'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 
        'margin': '3px', 'fontSize': '10px'
    }

# === MAIN LAYOUT ===
app.layout = html.Div([
    # === 1. Header ===
    dbc.Container([
        html.H1("India Meteorological Department", 
                className="text-center mb-4", 
                style={'color': '#2c3e50', 'marginTop': '20px'})
    ], fluid=True),

    # Main content in 2x2 grid
    dbc.Container([

        # === Top Row ===
        dbc.Row([
            # === 2. Top Left - Dashboard 2 (File Monitoring) ===
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.H4("File Monitoring Dashboard", className="mb-0")]),
                    dbc.CardBody([
                        html.Label("Select Date:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                        dcc.DatePickerSingle(id='date-picker-d2', date=datetime.now().date(), display_format='DD MMM YYYY', className='mb-3'),
                        html.Div([
                            html.Span("🔄 Auto-refresh: Every 5 minutes", style={'color': 'green', 'fontSize': '12px'}),
                            html.Span(id='last-update-d2', style={'marginLeft': '15px', 'fontSize': '10px', 'color': 'gray'})
                        ], className='mb-3'),
                        dcc.Interval(id='interval-refresh-d2', interval=5 * 60 * 1000, n_intervals=0),
                        html.Div(id='file-status-d2', style={'height': '300px', 'overflowY': 'auto'})
                    ])
                ], style={'height': '500px'})
            ], width=6),

            # === 3. Top Right - Dashboard 3 (Orbit Determination) ===
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.H4("Orbit Determination File Monitor", className="mb-0")]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.DatePickerSingle(id='date-picker-fax', date=date.today() - timedelta(days=2), display_format='YYYY-MM-DD', style={'fontSize': '14px'})
                            ], width=12)
                        ], className='mb-3'),
                        
                        html.H5("Reception", className="text-center", style={'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span("INSAT3DR", style={'fontSize': '16px', 'fontWeight': 'bold'})
                                ], id='3dr-box-fax', style=base_style_large()),
                                html.Div(id='3dr-filename-fax', style={'textAlign': 'center', 'fontSize': '12px', 'height': '30px', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INSAT3DS", style={'fontSize': '16px', 'fontWeight': 'bold'})
                                ], id='3ds-box-fax', style=base_style_large()),
                                html.Div(id='3ds-filename-fax', style={'textAlign': 'center', 'fontSize': '12px', 'height': '30px', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
                        
                        html.H5("Updation", className="text-center", style={'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span("INS3RM", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3rm-box-fax', style=base_style_small()),
                                html.Div(id='ins3rm-filename-fax', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3RR", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3rr-box-fax', style=base_style_small()),
                                html.Div(id='ins3rr-filename-fax', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3SM", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3sm-box-fax', style=base_style_small()),
                                html.Div(id='ins3sm-filename-fax', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3SR", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3sr-box-fax', style=base_style_small()),
                                html.Div(id='ins3sr-filename-fax', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
                        
                        html.Div("📝 Date picker shows the file date (2 days behind today by default)", 
                                style={'fontSize': '12px', 'color': '#7f8c8d', 'fontStyle': 'italic', 'textAlign': 'center'})
                    ], style={'height': '500px', 'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #dee2e6'})
                ], style={'height': '500px', 'marginBottom': '20px'})
            ], width=6)
        ]),

        # === Bottom Row ===
        dbc.Row([
            # === 4. Bottom Left - Dashboard 1 (Satellite Attitude) ===
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.H4("Satellite Attitude Visualization", className="mb-0")]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Satellite:", style={'fontSize': '12px'}),
                                dcc.Dropdown(id="satellite-dropdown-d1", 
                                           options=[{"label": s, "value": s} for s in SATELLITES], 
                                           value=SATELLITES[0], 
                                           style={'fontSize': '12px'})
                            ], width=4),
                            dbc.Col([
                                html.Label("Date:", style={'fontSize': '12px'}),
                                dcc.DatePickerSingle(id='date-picker-d1', 
                                                   date=datetime.now().date(), 
                                                   style={'fontSize': '12px', "marginTop": "15px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Time:", style={'fontSize': '12px'}),
                                dcc.Dropdown(id='time-dropdown-d1', 
                                           placeholder='Select Time', 
                                           style={'fontSize': '12px'})
                            ], width=4)
                        ], className="mb-3"),
                        dcc.Graph(id="attitude-graph-d1", style={'height': '250px'}),
                        dbc.Col([
                            dcc.Graph(id="yaw-graph", style={'height': '250px'}),
                            dcc.Graph(id="pitch-graph", style={'height': '250px'}),
                            dcc.Graph(id="roll-graph", style={'height': '250px'})
                        ])
                    ])
                ], style={'height': '1300px'})
            ], width=6),

            # === 5. Bottom Right - Dashboard 4 (Orbit Time Determination) ===
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([html.H4("Orbit Time File Monitor", className="mb-0")]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.DatePickerSingle(id='date-picker-obt', date=date.today(), display_format='YYYY-MM-DD', style={'fontSize': '14px'})
                            ], width=12)
                        ], className='mb-3'),
                        
                        html.H5("Reception", className="text-center", style={'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span("INSAT3DR", style={'fontSize': '16px', 'fontWeight': 'bold'})
                                ], id='3dr-box-obt', style=base_style_large()),
                                html.Div(id='3dr-filename-obt', style={'textAlign': 'center', 'fontSize': '12px', 'height': '30px', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INSAT3DS", style={'fontSize': '16px', 'fontWeight': 'bold'})
                                ], id='3ds-box-obt', style=base_style_large()),
                                html.Div(id='3ds-filename-obt', style={'textAlign': 'center', 'fontSize': '12px', 'height': '30px', 'marginTop': '10px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
                        
                        html.H5("Updation", className="text-center", style={'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span("INS3RM", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3rm-box-obt', style=base_style_small()),
                                html.Div(id='ins3rm-filename-obt', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3RR", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3rr-box-obt', style=base_style_small()),
                                html.Div(id='ins3rr-filename-obt', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3SM", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3sm-box-obt', style=base_style_small()),
                                html.Div(id='ins3sm-filename-obt', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                            html.Div([
                                html.Div([
                                    html.Span("INS3SR", style={'fontSize': '14px', 'fontWeight': 'bold'})
                                ], id='ins3sr-box-obt', style=base_style_small()),
                                html.Div(id='ins3sr-filename-obt', style={'textAlign': 'center', 'fontSize': '10px', 'height': '25px', 'marginTop': '8px'})
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
                        ], style={'display': 'flex', 'justifyContent': 'space-around'})
                    ], style={'height': '500px', 'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #dee2e6'})
                ])
            ], width=6)
        ])
    ], fluid=True, style={'backgroundColor': '#f5f5f5', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'})
])
# === CALLBACKS ===

# Dashboard 1 Callbacks
@app.callback(
    Output("time-dropdown-d1", "options"),
    [Input("satellite-dropdown-d1", "value"),
     Input("date-picker-d1", "date")]
)
def update_time_options_d1(sat, selected_date):
    if not sat or not selected_date:
        return []
    return get_time_options(sat, selected_date)

@app.callback(
    [Output("attitude-graph-d1", "figure"),
    Output("yaw-graph", "figure"),
    Output("pitch-graph", "figure"),
    Output("roll-graph", "figure")],
    [Input("satellite-dropdown-d1", "value"),
     Input("date-picker-d1", "date"),
     Input("time-dropdown-d1", "value")]
)
def update_attitude_graph_d1(sat, date_str, time_str):
    empty_fig = go.Figure()
    
    if not (sat and date_str and time_str):
        return empty_fig.update_layout(title="Select satellite, date, and time")
    
    try:
        dt_obj = datetime.strptime(f"{date_str}", "%Y-%m-%d")
        filename = f"{FILE_PREFIX[sat]}_{dt_obj.strftime('%d%b%Y').upper()}_{time_str}_att.dat.GPD_utc"
        file_path = os.path.join(BASE_DIR_SAT, sat, filename)
        if not os.path.exists(file_path):
            file_path = get_latest_file(sat)
    except Exception:
        file_path = get_latest_file(sat)
    
    if not file_path:
        return empty_fig.update_layout(title="No data available")
    
    try:
        df = read_gpd_utc_dat(file_path)
        if df.empty:
            return empty_fig.update_layout(title="No data found")
        
        df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
        
        fig = go.Figure([
            go.Scatter(x=df['timestamp'], y=df['yaw'], name='Yaw', mode='lines'),
            go.Scatter(x=df['timestamp'], y=df['pitch'], name='Pitch', mode='lines'),
            go.Scatter(x=df['timestamp'], y=df['roll'], name='Roll', mode='lines'),
        ])

        fig.update_layout(
            title=f"Attitude Data: {os.path.basename(file_path)}",
            xaxis_title="Time",
            yaxis_title="Angle (degrees)",
            legend_title="Parameters",
            hovermode="x unified",
            height=280,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        fig_yaw = go.Figure([go.Scatter(x=df['timestamp'], y=df['yaw'], name='Yaw', line=dict(color='blue'))])
        fig_yaw.update_layout(title="Yaw", xaxis_title="Time", yaxis_title="Degrees", height=300, hovermode="x unified")
        
        fig_pitch = go.Figure([go.Scatter(x=df['timestamp'], y=df['pitch'], name='Pitch', line=dict(color='red'))])
        fig_pitch.update_layout(title="Pitch", xaxis_title="Time", yaxis_title="Degrees", height=300, hovermode="x unified")
        
        fig_roll = go.Figure([go.Scatter(x=df['timestamp'], y=df['roll'], name='Roll', line=dict(color='green'))])
        fig_roll.update_layout(title="Roll", xaxis_title="Time", yaxis_title="Degrees", height=300, hovermode="x unified")
        return fig, fig_yaw, fig_pitch, fig_roll
    except Exception as e:
        return empty_fig.update_layout(title=f"Error loading data: {str(e)}")

# Dashboard 2 Callbacks
@app.callback(
    [Output('file-status-d2', 'children'),
     Output('last-update-d2', 'children')],
    [Input('date-picker-d2', 'date'), 
     Input('interval-refresh-d2', 'n_intervals')]
)
def update_file_status_d2(date_str, n_intervals):
    current_time = datetime.now().strftime('%H:%M:%S')
    
    if not date_str:
        return "No date selected.", f"Last updated: {current_time}"
    
    try:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        elif hasattr(date_str, 'year'):
            if isinstance(date_str, date) and not isinstance(date_str, datetime):
                date_obj = datetime.combine(date_str, datetime.min.time())
            else:
                date_obj = date_str
        else:
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
    except (ValueError, TypeError, AttributeError) as e:
        return f"Invalid date format: {e}", f"Last updated: {current_time}"
    
    try:
        available_set = load_log_file()
    except Exception as e:
        return f"Error loading log file: {e}", f"Last updated: {current_time}"
    
    status_components = []
    for utc in TIME_INTERVALS:
        try:
            availability = check_file_availability(date_obj, utc, available_set)
            status_components.append(html.Div([
                html.H6(f"{utc} UTC", style={'margin': '5px 0'}),
                html.Div(generate_file_boxes(availability))
            ], className='mb-2'))
        except Exception as e:
            status_components.append(html.Div([
                html.H6(f"{utc} UTC - Error: {e}", style={'margin': '5px 0'})
            ], className='mb-2'))
    
    return status_components, f"Last updated: {current_time}"

# === Callback for FAX Dashboard 3===
@app.callback(
    [Output('ins3rm-box-fax', 'style'),
     Output('ins3rr-box-fax', 'style'),
     Output('ins3sm-box-fax', 'style'),
     Output('ins3sr-box-fax', 'style'),
     Output('3dr-box-fax', 'style'),
     Output('3ds-box-fax', 'style'),
     Output('3dr-filename-fax', 'children'),
     Output('3ds-filename-fax', 'children'),
     Output('ins3rm-filename-fax', 'children'),
     Output('ins3rr-filename-fax', 'children'),
     Output('ins3sm-filename-fax', 'children'),
     Output('ins3sr-filename-fax', 'children')],
    [Input('date-picker-fax', 'date')]
)
def update_fax_dashboard(selected_date):
    if not selected_date:
        selected_date = date.today() - timedelta(days=2)  # Changed default fallback
    else:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    filenames = {
        'INS3RM': get_matching_filename_fax(selected_date, 'INS3RM'),
        'INS3RR': get_matching_filename_fax(selected_date, 'INS3RR'),
        'INS3SM': get_matching_filename_fax(selected_date, 'INS3SM'),
        'INS3SR': get_matching_filename_fax(selected_date, 'INS3SR'),
        '3DR': get_matching_filename_fax(selected_date, '3DR'),
        '3DS': get_matching_filename_fax(selected_date, '3DS')
    }

    green_color = '#27ae60'
    red_color = '#e74c3c'

    styles = [
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3RM'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3RR'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3SM'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3SR'] != 'Not Found' else red_color},
        {**base_style_large(), 'backgroundColor': green_color if filenames['3DR'] != 'Not Found' else red_color},
        {**base_style_large(), 'backgroundColor': green_color if filenames['3DS'] != 'Not Found' else red_color}
    ]

    return styles + [filenames[k] for k in ['3DR', '3DS', 'INS3RM', 'INS3RR', 'INS3SM', 'INS3SR']]


# === Callback for OBT Dashboard 4 ===
@app.callback(
    [Output('ins3rm-box-obt', 'style'),
     Output('ins3rr-box-obt', 'style'),
     Output('ins3sm-box-obt', 'style'),
     Output('ins3sr-box-obt', 'style'),
     Output('3dr-box-obt', 'style'),
     Output('3ds-box-obt', 'style'),
     Output('3dr-filename-obt', 'children'),
     Output('3ds-filename-obt', 'children'),
     Output('ins3rm-filename-obt', 'children'),
     Output('ins3rr-filename-obt', 'children'),
     Output('ins3sm-filename-obt', 'children'),
     Output('ins3sr-filename-obt', 'children')],
    [Input('date-picker-obt', 'date')]
)
def update_obt_dashboard(selected_date):
    if not selected_date:
        selected_date = date.today()
    else:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    filenames = {key: get_matching_filename_obt(selected_date, key) for key in LOG_FILES_OBT.keys()}

    green_color = '#27ae60'
    red_color = '#e74c3c'

    styles = [
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3RM'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3RR'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3SM'] != 'Not Found' else red_color},
        {**base_style_small(), 'backgroundColor': green_color if filenames['INS3SR'] != 'Not Found' else red_color},
        {**base_style_large(), 'backgroundColor': green_color if filenames['3DR'] != 'Not Found' else red_color},
        {**base_style_large(), 'backgroundColor': green_color if filenames['3DS'] != 'Not Found' else red_color}
    ]

    return styles + [filenames[k] for k in ['3DR', '3DS', 'INS3RM', 'INS3RR', 'INS3SM', 'INS3SR']]

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)