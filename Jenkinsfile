pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo '========================================='
                echo 'Stage 1: Building Docker Image'
                echo '========================================='
                sh 'docker build -t campus-maintenance-ci .'
            }
        }

        stage('Test') {
            steps {
                echo '========================================='
                echo 'Stage 2: Running Automated Pytest Suite'
                echo '========================================='
                sh 'docker run --rm campus-maintenance-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy with Ansible') {
            steps {
                echo '========================================='
                echo 'Stage 3: Deploying Container with Ansible'
                echo '========================================='
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
