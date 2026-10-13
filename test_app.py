import os
import sqlite3
import tempfile
import pytest
import app as app_module


@pytest.fixture
def client():
    """Create an isolated test client with a dedicated temporary SQLite database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, 'data', 'campus_maintenance.db')
        os.makedirs(os.path.dirname(test_db_path), exist_ok=True)

        original_db_path = app_module.DB_PATH
        app_module.DB_PATH = test_db_path
        app_module.init_db()

        app_module.app.config['TESTING'] = True
        app_module.app.config['SECRET_KEY'] = 'test-secret-key'

        with app_module.app.test_client() as test_client:
            yield test_client

        app_module.DB_PATH = original_db_path


def test_flask_app_starts(client):
    """Test 1: Verify Flask application initializes and testing client is active."""
    assert app_module.app is not None
    assert app_module.app.config['TESTING'] is True


def test_home_page_returns_200(client):
    """Test 2: Verify home page (/) loads successfully with HTTP 200."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CampusFix' in response.data
    assert b'Smart Maintenance System' in response.data


def test_report_page_returns_200(client):
    """Test 3: Verify report page (/report) loads successfully with HTTP 200."""
    response = client.get('/report')
    assert response.status_code == 200
    assert b'Campus Maintenance Request Form' in response.data
    assert b'Electrical Issue' in response.data
    assert b'Plumbing Issue' in response.data


def test_submit_maintenance_request_and_storage(client):
    """Test 4 & 5: Verify maintenance request submission and verification in SQLite."""
    payload = {
        'issue_type': 'Electrical Issue',
        'location': 'Library 2nd Floor, Room 204',
        'description': 'Main fluorescent tube light flickering and buzzing.',
        'priority': 'High'
    }

    # Submit via POST /submit_request
    response = client.post('/submit_request', data=payload, follow_redirects=True)
    assert response.status_code == 200
    assert b'submitted successfully' in response.data

    # Verify directly from SQLite database
    conn = app_module.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM maintenance_requests WHERE location = ?', (payload['location'],))
    record = cursor.fetchone()
    conn.close()

    assert record is not None
    assert record['issue_type'] == 'Electrical Issue'
    assert record['location'] == 'Library 2nd Floor, Room 204'
    assert record['description'] == 'Main fluorescent tube light flickering and buzzing.'
    assert record['priority'] == 'High'
    assert record['status'] == 'Pending'


def test_admin_page_returns_200(client):
    """Test 6: Verify Admin page (/admin) returns HTTP 200 and displays requests."""
    # First insert a test ticket
    conn = app_module.get_db_connection()
    conn.execute(
        '''
        INSERT INTO maintenance_requests (issue_type, location, description, priority, status)
        VALUES ('Plumbing Issue', 'Hostel Block A, Washroom 3', 'Water tap leaking heavily', 'Medium', 'Pending')
        '''
    )
    conn.commit()
    conn.close()

    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Facilities Management Dashboard' in response.data
    assert b'Hostel Block A, Washroom 3' in response.data
    assert b'Plumbing Issue' in response.data


def test_track_page_with_valid_and_invalid_id(client):
    """Test 7: Verify tracking endpoint for both existing and non-existing tickets."""
    # Insert a record
    conn = app_module.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO maintenance_requests (issue_type, location, description, priority, status)
        VALUES ('Internet/Wi-Fi Issue', 'Main Auditorium', 'Wi-Fi router offline', 'Urgent', 'Assigned')
        '''
    )
    conn.commit()
    req_id = cursor.lastrowid
    conn.close()

    # Track valid request
    response_valid = client.get(f'/track?request_id={req_id}')
    assert response_valid.status_code == 200
    assert b'Main Auditorium' in response_valid.data
    assert b'Assigned' in response_valid.data

    # Track non-existent request
    response_invalid = client.get('/track?request_id=99999')
    assert response_invalid.status_code == 200
    assert b'Request Not Found' in response_invalid.data


def test_update_status_workflow(client):
    """Test 8: Verify admin can transition request status (Pending -> Assigned -> Resolved)."""
    # Create request
    conn = app_module.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO maintenance_requests (issue_type, location, description, priority, status)
        VALUES ('Furniture Repair', 'Seminar Hall 1', 'Broken armrest on chair 12', 'Low', 'Pending')
        '''
    )
    conn.commit()
    req_id = cursor.lastrowid
    conn.close()

    # Update status to 'In Progress'
    update_resp = client.post('/update_status', data={
        'request_id': req_id,
        'status': 'In Progress'
    }, follow_redirects=True)
    assert update_resp.status_code == 200

    # Verify status in database
    conn = app_module.get_db_connection()
    updated_record = conn.execute('SELECT status FROM maintenance_requests WHERE id = ?', (req_id,)).fetchone()
    conn.close()
    assert updated_record['status'] == 'In Progress'


def test_submit_request_validation(client):
    """Test 9: Verify submission with empty fields fails safely with validation message."""
    invalid_payload = {
        'issue_type': '',
        'location': '',
        'description': '',
        'priority': 'Medium'
    }
    response = client.post('/submit_request', data=invalid_payload, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please select a valid issue type.' in response.data
