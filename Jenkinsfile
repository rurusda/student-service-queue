
pipeline {
    agent {
        label 'docker-agent'
    }

    environment {
        COMPOSE_PROJECT_NAME = 'student-service-queue'
    }
    
    options {
        timestamps()
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                checkout scm
                echo 'Source code berhasil diambil dari GitHub.'
            }
        }

        stage('Code Validation') {
            steps {
                sh 'python3 -m py_compile backend/app.py'
                sh 'docker compose config -q'
                echo 'Validasi kode dan Docker Compose berhasil.'
            }
        }

        stage('Build and Deploy') {
            steps {
                sh 'docker compose up -d --build'
                echo 'Build dan deployment berhasil dijalankan.'
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for i in $(seq 1 10); do
                        if curl -fsS http://localhost:5001/health; then
                            echo "Backend API aktif."
                            exit 0
                        fi
                        echo "Menunggu backend aktif..."
                        sleep 3
                    done

                    echo "Backend gagal memberikan respons."
                    exit 1
                '''

                sh 'curl -fsS http://localhost:8081'
            }
        }
    }

    post {
        success {
            echo 'CI/CD SUCCESS: Student Service Queue berhasil di-deploy!'
        }

        failure {
            echo 'CI/CD FAILED: Periksa kembali log Jenkins.'
        }

        always {
            sh 'docker compose ps || true'
        }
    }
}
