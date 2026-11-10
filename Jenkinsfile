
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
                    set -e

                    echo "Memeriksa kesehatan Backend API..."

                    for i in $(seq 1 10); do
                        if docker compose exec -T backend python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5001/health', timeout=3).read().decode())"; then
                            echo "Backend API aktif."
                            break
                        fi

                        if [ "$i" -eq 10 ]; then
                            echo "Backend gagal memberikan respons."
                            docker compose logs --tail=50 backend
                            exit 1
                        fi

                        echo "Menunggu backend aktif..."
                        sleep 3
                    done

                    echo "Memeriksa kesehatan Frontend..."

                    docker compose exec -T frontend wget -q -O /dev/null http://127.0.0.1/

                    echo "Frontend berhasil diakses."
                    echo "Semua Health Check berhasil."
                '''
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
