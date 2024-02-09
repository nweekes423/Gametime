pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh 'python manage.py test'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Add deployment steps here
                    // e.g., collectstatic, migrate, etc.
                }
            }
        }
    }
}

