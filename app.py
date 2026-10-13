import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'campus-maintenance-devops-secret-key-2026')

# Database configuration: Always use data/campus_maintenance.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULT_DB_PATH = os.path.join(DATA_DIR, 'campus_maintenance.db')
DB_PATH = os.environ.get('CAMPUS_MAINTENANCE_DB', DEFAULT_DB_PATH)

VALID_ISSUE_TYPES = [
    'Electrical Issue',
    'Plumbing Issue',
    'Classroom/Lab Equipment',
    'Internet/Wi-Fi Issue',
    'Furniture Repair',
    'Cleaning Issue',
    'Other'
]

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
VALID_STATUSES = ['Pending', 'Assigned', 'In Progress', 'Resolved']


def get_db_connection():
    """Create and return a thread-safe connection to the SQLite database."""
    db_directory = os.path.dirname(DB_PATH)
    if db_directory:
        os.makedirs(db_directory, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ensure data directory and maintenance_requests table exist."""
    db_directory = os.path.dirname(DB_PATH)
    if db_directory:
        os.makedirs(db_directory, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Initialize database automatically on startup
init_db()


@app.template_filter('format_datetime')
def format_datetime(value):
    """Format timestamp for clean UI presentation."""
    if not value:
        return 'N/A'
    try:
        # SQLite CURRENT_TIMESTAMP returns 'YYYY-MM-DD HH:MM:SS'
        dt = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%b %d, %Y - %I:%M %p')
    except Exception:
        return str(value)


@app.route('/')
def index():
    """Campus maintenance portal home page."""
    try:
        conn = get_db_connection()
        total_count = conn.execute('SELECT COUNT(*) FROM maintenance_requests').fetchone()[0]
        resolved_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Resolved'").fetchone()[0]
        active_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status IN ('Pending', 'Assigned', 'In Progress')").fetchone()[0]
        conn.close()
    except Exception:
        total_count = 0
        resolved_count = 0
        active_count = 0

    return render_template('index.html',
                           total_count=total_count,
                           resolved_count=resolved_count,
                           active_count=active_count)


@app.route('/report')
def report():
    """Report campus maintenance issue page."""
    return render_template('report.html',
                           issue_types=VALID_ISSUE_TYPES,
                           priorities=VALID_PRIORITIES)


@app.route('/submit_request', methods=['POST'])
def submit_request():
    """Handle maintenance request submission with validation."""
    issue_type = request.form.get('issue_type', '').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'Medium').strip()

    # Input validation
    errors = []
    if not issue_type or issue_type not in VALID_ISSUE_TYPES:
        errors.append('Please select a valid issue type.')
    if not location:
        errors.append('Campus location/room number is required.')
    if not description:
        errors.append('A short description of the issue is required.')
    if priority not in VALID_PRIORITIES:
        priority = 'Medium'

    if errors:
        for err in errors:
            flash(err, 'danger')
        return redirect(url_for('report'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO maintenance_requests (issue_type, location, description, priority, status)
            VALUES (?, ?, ?, ?, 'Pending')
            ''',
            (issue_type, location, description, priority)
        )
        conn.commit()
        request_id = cursor.lastrowid
        conn.close()

        flash(f'Maintenance request submitted successfully! Your Request ID is #{request_id}.', 'success')
        return redirect(url_for('track', request_id=request_id))
    except Exception as e:
        flash(f'An error occurred while submitting your request: {str(e)}', 'danger')
        return redirect(url_for('report'))


@app.route('/track', methods=['GET', 'POST'])
def track():
    """Track maintenance request status by ID."""
    request_id = request.args.get('request_id')
    if request.method == 'POST':
        request_id = request.form.get('request_id')

    request_item = None
    searched_id = None
    not_found = False

    if request_id:
        searched_id = str(request_id).strip().lstrip('#')
        try:
            req_id_int = int(searched_id)
            conn = get_db_connection()
            request_item = conn.execute(
                'SELECT * FROM maintenance_requests WHERE id = ?',
                (req_id_int,)
            ).fetchone()
            conn.close()
            if not request_item:
                not_found = True
        except (ValueError, TypeError):
            not_found = True

    return render_template('track.html',
                           request_item=request_item,
                           searched_id=searched_id,
                           not_found=not_found)


@app.route('/admin')
def admin():
    """Admin dashboard with summary metrics and all maintenance requests."""
    conn = get_db_connection()

    # Summary metrics
    total_requests = conn.execute('SELECT COUNT(*) FROM maintenance_requests').fetchone()[0]
    pending_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Pending'").fetchone()[0]
    assigned_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Assigned'").fetchone()[0]
    in_progress_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'In Progress'").fetchone()[0]
    resolved_count = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Resolved'").fetchone()[0]

    # Optional status filter
    filter_status = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    sql = 'SELECT * FROM maintenance_requests WHERE 1=1'
    params = []

    if filter_status and filter_status in VALID_STATUSES:
        sql += ' AND status = ?'
        params.append(filter_status)

    if search_query:
        sql += ' AND (location LIKE ? OR description LIKE ? OR issue_type LIKE ? OR id = ?)'
        wildcard = f'%{search_query}%'
        search_id = search_query.lstrip('#')
        search_id_val = int(search_id) if search_id.isdigit() else -1
        params.extend([wildcard, wildcard, wildcard, search_id_val])

    sql += ' ORDER BY id DESC'
    requests_list = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template('admin.html',
                           requests=requests_list,
                           total_requests=total_requests,
                           pending_count=pending_count,
                           assigned_count=assigned_count,
                           in_progress_count=in_progress_count,
                           resolved_count=resolved_count,
                           filter_status=filter_status,
                           search_query=search_query,
                           valid_statuses=VALID_STATUSES)


@app.route('/update_status', methods=['POST'])
def update_status():
    """Update maintenance request status (Pending -> Assigned -> In Progress -> Resolved)."""
    request_id = request.form.get('request_id', '').strip()
    new_status = request.form.get('status', '').strip()

    if not request_id or new_status not in VALID_STATUSES:
        flash('Invalid status update parameters.', 'danger')
        return redirect(url_for('admin'))

    try:
        req_id_int = int(request_id)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE maintenance_requests SET status = ? WHERE id = ?',
            (new_status, req_id_int)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        if rows_affected > 0:
            flash(f'Request #{req_id_int} status updated to "{new_status}" successfully!', 'success')
        else:
            flash(f'Request #{req_id_int} not found.', 'warning')
    except (ValueError, TypeError) as e:
        flash(f'Failed to update status: {str(e)}', 'danger')

    return redirect(url_for('admin'))


@app.route('/api/stats')
def api_stats():
    """API endpoint providing current maintenance statistics."""
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM maintenance_requests').fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Pending'").fetchone()[0]
    assigned = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Assigned'").fetchone()[0]
    in_progress = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'In Progress'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Resolved'").fetchone()[0]
    conn.close()

    return jsonify({
        'total': total,
        'pending': pending,
        'assigned': assigned,
        'in_progress': in_progress,
        'resolved': resolved
    })


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error_message='The requested page could not be found.'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', error_message='An unexpected internal error occurred.'), 500


if __name__ == '__main__':
    # Make sure DB is ready
    init_db()
    # Flask application listening on 0.0.0.0:5000 as specified
    app.run(host='0.0.0.0', port=5000, debug=False)
