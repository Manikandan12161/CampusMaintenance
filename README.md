# SMART CAMPUS MAINTENANCE REQUEST SYSTEM

A professional college-level DevOps engineering project featuring a functional **Python Flask** web application, **SQLite** persistent database, **Docker** containerization, **Pytest** automated testing, **Jenkins** CI/CD pipeline automation, and **Ansible** configuration management & deployment.

Developed for university facility tracking and DevOps laboratory demonstrations.

- **GitHub Profile**: [Manikandan12161](https://github.com/Manikandan12161)
- **Repository Name**: `CampusMaintenance`

---

## 1. Project Overview

The **Smart Campus Maintenance Request System** ("CampusFix") streamlines facility issue management across university academic blocks, laboratories, hostels, and administrative facilities. Students and faculty can instantly submit facility breakdown reports, receive tracking identifiers, and monitor repairs in real time. Administrators and facility engineers utilize a central dashboard to monitor incoming tickets, assess priorities, assign technicians, and advance tickets from submission through resolution.

### Key Highlights
- **Lightweight & Self-Contained**: Pure Python Flask backend with zero external database dependencies (uses embedded SQLite).
- **Persistent Data Storage**: Uses a Docker Volume (`campus_maintenance_data`) to ensure SQLite database records survive container recreation or failure.
- **Enterprise DevOps Pipeline**: Clean separation between application runtime traffic and DevOps automation (Developer &rarr; GitHub &rarr; Jenkins &rarr; Docker Build &rarr; Pytest &rarr; Ansible &rarr; Production Container).

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) | Modern institutional UI, responsive layout, progress steppers, real-time filtering |
| **Backend** | Python 3.11, Flask 3.x | RESTful routing, input validation, SQL query execution, templating |
| **Database** | SQLite 3 | Lightweight relational database stored at `data/campus_maintenance.db` |
| **Automated Testing** | Pytest 8.x | Automated unit, route, and database integration tests |
| **Containerization** | Docker (`python:3.11-slim`) | Standardized runtime container (`campus-maintenance-ci`) |
| **Storage Persistence**| Docker Volume (`campus_maintenance_data`) | Host-independent database persistence mounted to `/app/data` |
| **CI/CD Pipeline** | Jenkins (`Jenkinsfile`) | Automated Build, Test, and Deploy stages |
| **Configuration Mgmt** | Ansible (`campus-deploy.yml`) | Container lifecycle management via `community.docker.docker_container` |
| **Version Control** | Git & GitHub | Source code tracking and collaboration |

---

## 3. System Architecture & Workflows

### A. Application Runtime Workflow (User / Student & Admin)
Submitting a maintenance ticket is an application-level transaction and **does NOT** trigger Jenkins or the CI/CD pipeline.

```
Student / User
      ↓
Open Web Portal (Home / Report)
      ↓
Select Issue Category & Enter Campus Location
      ↓
Enter Description & Choose Priority (Low / Medium / High / Urgent)
      ↓
Submit Form (POST /submit_request)
      ↓
Flask Backend Validation
      ↓
SQLite Database (data/campus_maintenance.db)
      ↓
Unique Request ID Generated (#REQ)
      ↓
Student Tracks Live Status (Pending → Assigned → In Progress → Resolved)
      ↓
Admin Dashboard (/admin)
      ↓
Admin Reviews & Updates Status (POST /update_status)
      ↓
SQLite Updated & Changes Reflected Live
```

---

### B. DevOps CI/CD Automation Workflow

```
Developer (Code Changes)
      ↓
Git Commit & Push to GitHub (Manikandan12161/CampusMaintenance)
      ↓
Jenkins CI Server (Webhook / SCM Trigger)
      ↓
Stage 1: Build Docker Image
   [docker build -t campus-maintenance-ci .]
      ↓
Stage 2: Run Pytest Test Suite
   [docker run --rm campus-maintenance-ci python -m pytest test_app.py]
      ↓ (Proceeds ONLY if all tests pass)
Stage 3: Deploy with Ansible Playbook
   [docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /campus-deploy.yml]
      ↓
Ansible Orchestrates Container
   - Ensures Docker Volume: campus_maintenance_data
   - Runs Container: campus-maintenance-ansible
   - Maps Port: 5002:5000
   - Mounts Volume: campus_maintenance_data:/app/data
      ↓
Flask Application Live & Serving Traffic
      ↓
Data Persisted in SQLite on Docker Volume
```

---

## 4. Project Directory Structure

```
CampusMaintenance/
│
├── app.py                     # Main Flask backend application & SQLite controller
├── requirements.txt           # Python dependencies (Flask, pytest)
├── Dockerfile                 # Container image specification (python:3.11-slim)
├── Jenkinsfile                # Jenkins CI/CD declarative pipeline definition
├── campus-deploy.yml          # Ansible playbook for Docker container deployment
├── test_app.py                # Pytest automated test suite
├── .gitignore                 # Excludes database, caches, virtual environments
├── README.md                  # Comprehensive project documentation & lab viva guide
│
├── templates/                 # Jinja2 HTML templates
│   ├── index.html             # Campus portal home page & live summary counters
│   ├── report.html            # Maintenance issue reporting form
│   ├── track.html             # Request status tracker with 4-step progress stepper
│   ├── admin.html             # Facilities admin dashboard & inline status updater
│   └── login.html             # Restricted Admin authentication login screen
│
├── static/                    # Frontend styling & client logic
│   ├── style.css              # Custom responsive institutional theme
│   └── script.js              # Alerts, copy buttons, live table filter
│
└── data/                      # Dedicated SQLite database directory
    └── .gitkeep               # Keeps folder tracked in Git (database file ignored)
```

> **Strict Rule Enforced**: The database is always stored at `data/campus_maintenance.db` (or `/app/data/campus_maintenance.db` inside the container), never in the root directory.

---

## 5. Functional Features

### Student / User Features
- **Intuitive Homepage**: Clean overview with quick access buttons and live counts of total, active, and resolved campus requests.
- **Maintenance Reporting**:
  - Issue categories: *Electrical Issue, Plumbing Issue, Classroom/Lab Equipment, Internet/Wi-Fi Issue, Furniture Repair, Cleaning Issue, Other*.
  - Specific location capture (Building, Wing, Room Number, Lab).
  - Detailed description with input length checks.
  - Priority selection: *Low, Medium, High, Urgent*.
- **Instant Request ID**: Upon submission, a unique ticket ID is generated and returned with one-click clipboard copying.
- **Visual Status Tracking**: Interactive 4-step status progress bar illustrating:
  1. `Pending Review`
  2. `Assigned to Technician`
  3. `In Progress / Repair Underway`
  4. `Resolved`

### Facility Admin Features (Protected with Authentication)
- **Role-Based Access Control**:
  - Only authenticated administrators can access `/admin` and modify ticket statuses via `/update_status`.
  - Unauthenticated access attempts automatically redirect to `/login` with a security warning.
  - **Default Evaluation Credentials**:
    - **Username**: `admin`
    - **Password**: `admin123`
- **4 Key Summary KPI Cards**:
  - **Total Requests**
  - **Pending**
  - **Assigned**
  - **Resolved**
- **Dynamic Filter Pills**: Instantly isolate tickets by status (*All, Pending, Assigned, In Progress, Resolved*).
- **Client-Side Live Filter**: Search by keyword, building, or room number without reloading the page.
- **Inline Status Transitions**: Dropdown allowing admins to update status between any lifecycle state with immediate SQLite persistence.
- **Session Logout**: One-click session termination (`/logout`) returning to public mode.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.9+ or Python 3.11 installed
- Git installed

### Step-by-Step Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Manikandan12161/CampusMaintenance.git
   cd CampusMaintenance
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # On Linux/macOS:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   - Web Portal: `http://localhost:5000`
   - Report Ticket: `http://localhost:5000/report`
   - Track Ticket: `http://localhost:5000/track`
   - Admin Dashboard: `http://localhost:5000/admin`

*(The SQLite database and `data/` directory will be created automatically on initial startup)*

---

## 7. How to Run Automated Pytest Tests

The automated test suite verifies Flask initialization, route availability, database insertions, ID queries, status updates, and input validation. The tests use isolated temporary databases and **do not depend on pre-existing data**.

```bash
# Run tests directly
python -m pytest test_app.py

# Run tests with verbose output
python -m pytest test_app.py -v
```

### Expected Output:
```
test_app.py::test_flask_app_starts PASSED                     [ 12%]
test_app.py::test_home_page_returns_200 PASSED                [ 25%]
test_app.py::test_report_page_returns_200 PASSED              [ 37%]
test_app.py::test_submit_maintenance_request_and_storage PASSED [ 50%]
test_app.py::test_admin_page_returns_200 PASSED               [ 62%]
test_app.py::test_track_page_with_valid_and_invalid_id PASSED   [ 75%]
test_app.py::test_update_status_workflow PASSED               [ 87%]
test_app.py::test_submit_request_validation PASSED            [100%]

======================== 8 passed in 0.66s ========================
```

---

## 8. Docker Containerization

### A. Build the Docker Image
```bash
docker build -t campus-maintenance-ci .
```

### B. Run Automated Tests Inside Docker
Ensure zero environment discrepancies by running the Pytest suite in an ephemeral container:
```bash
docker run --rm campus-maintenance-ci python -m pytest test_app.py
```

### C. Run the Docker Container with Docker Volume
Run the container using the persistent volume `campus_maintenance_data`:
```bash
# 1. Create the persistent Docker volume
docker volume create campus_maintenance_data

# 2. Launch the application container
docker run -d \
  --name campus-maintenance-ansible \
  -p 5002:5000 \
  -v campus_maintenance_data:/app/data \
  --restart unless-stopped \
  campus-maintenance-ci
```

### D. Verify Deployment
Open your web browser and navigate to:
```
http://localhost:5002
```

---

## 9. Understanding the Docker Volume for SQLite Persistence

### Why Docker Volumes Matter in DevOps
By default, Docker containers are **ephemeral** (stateless). Any files written inside a container are destroyed when the container is stopped and removed (`docker rm`).

In this project:
- SQLite stores data in a single file: `data/campus_maintenance.db`.
- Inside the container, this maps to `/app/data/campus_maintenance.db`.
- We mount the Docker Volume `campus_maintenance_data` to `/app/data`:
  ```bash
  -v campus_maintenance_data:/app/data
  ```
- **Result**: Even if `campus-maintenance-ansible` is stopped, deleted (`docker rm -f`), or upgraded to a new Docker image version, the database stored in `campus_maintenance_data` remains intact. When the container starts again, all campus maintenance requests remain preserved!

---

## 10. Jenkins CI/CD Pipeline

The `Jenkinsfile` implements a declarative pipeline with 3 sequential stages:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo '=== Stage 1: Building Docker Image ==='
                sh 'docker build -t campus-maintenance-ci .'
            }
        }

        stage('Test') {
            steps {
                echo '=== Stage 2: Running Automated Pytest Suite ==='
                sh 'docker run --rm campus-maintenance-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo '=== Stage 3: Deploying Container with Ansible ==='
                sh 'docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /campus-deploy.yml'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Campus Maintenance CI/CD Pipeline Completed Successfully!'
        }
        failure {
            echo 'FAILURE: Campus Maintenance CI/CD Pipeline Failed!'
        }
    }
}
```

### How Jenkins Executes:
1. **Stage 1 (Build)**: Jenkins reads the Dockerfile, builds the image, and tags it `campus-maintenance-ci`.
2. **Stage 2 (Test)**: Jenkins spins up an isolated temporary container to run `python -m pytest test_app.py`. If any test fails, the build halts immediately, preventing broken code from reaching production.
3. **Stage 3 (Deploy)**: Jenkins invokes the Ansible control container (`ansible-docker-lab`) to execute `campus-deploy.yml`, updating the running production container with zero data loss.
4. **Post Notifications**: Prints explicit success/failure completion banners.

---

## 11. Ansible Container Deployment

The `campus-deploy.yml` playbook manages container lifecycle states declaratively:

```yaml
---
- name: Deploy Smart Campus Maintenance Request System Container
  hosts: all
  become: false
  tasks:
    - name: Ensure Docker volume for persistent SQLite database exists
      community.docker.docker_volume:
        name: campus_maintenance_data
        state: present

    - name: Deploy Campus Maintenance application container
      community.docker.docker_container:
        name: campus-maintenance-ansible
        image: campus-maintenance-ci
        state: "{{ container_state | default('started') }}"
        restart_policy: unless-stopped
        ports:
          - "5002:5000"
        volumes:
          - "campus_maintenance_data:/app/data"
        env:
          PYTHONUNBUFFERED: "1"
          FLASK_ENV: "production"
```

### How Ansible Works:
- **Idempotency**: If the container is already running with the exact configuration and latest image, Ansible makes no unnecessary disruptions. If the image was updated by Jenkins Stage 1, Ansible seamlessly stops the older container and starts the new one.
- **Volume Association**: Guarantees that `campus_maintenance_data` is mounted to `/app/data`.

---

## 12. College DevOps Viva / Examination Q&A Guide

**Q1: Why use SQLite instead of MySQL or PostgreSQL for this DevOps project?**
> *Answer*: SQLite is a serverless, self-contained relational database requiring zero external service setup. It demonstrates volume mounting, database file locking, and container persistence cleanly without adding unnecessary resource overhead to the lab environment.

**Q2: What is the difference between Application Flow and CI/CD Flow?**
> *Answer*: The application flow represents end-user runtime requests (a student reporting a broken lamp &rarr; Flask handles HTTP POST &rarr; SQLite stores record). The CI/CD flow is developer-triggered automation (code commit &rarr; Jenkins builds image &rarr; Pytest validates code &rarr; Ansible deploys container). Submitting a maintenance ticket does not trigger Jenkins.

**Q3: How does Pytest run inside Docker during CI?**
> *Answer*: We execute `docker run --rm campus-maintenance-ci python -m pytest test_app.py`. The `--rm` flag ensures the container is removed immediately after running tests. Because all dependencies and application code are baked into the image, tests execute in an environment identical to production.

**Q4: How does data persist when the container is deleted?**
> *Answer*: By mounting the named Docker volume `campus_maintenance_data:/app/data`. Named volumes exist on the Docker host filesystem outside the container union filesystem lifecycle. Removing or recreating the container does not delete the named volume.

**Q5: Why run Ansible via `docker exec ansible-docker-lab`?**
> *Answer*: In modern containerized DevOps labs, Ansible often runs inside a dedicated controller container (`ansible-docker-lab`) with all required Python libraries and Ansible collections (`community.docker`) pre-configured. Jenkins delegates the deployment step to this controller.

---

## 13. License & Authorship

Developed by **[Manikandan12161](https://github.com/Manikandan12161)** for DevOps Laboratory & Academic Demonstration.
Licensed under the MIT License.
