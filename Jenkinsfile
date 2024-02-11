pipeline {
    agent any

    environment {
        VENV = '/Users/will/Gametime/nba_notifier/venv'  // Change this to the appropriate virtual environment path
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Activate Virtual Environment') {
            steps {
                script {
                    // Activate the virtual environment
                    sh "source ${VENV}/bin/activate"
                }
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
                    // Use 'withCredentials' to securely access the GitHub secret
                    withCredentials([string(credentialsId: 'Secret-ID', variable: 'GITHUB_SECRET')]) {
                        // Validate the GitHub secret in the payload
                        validateGithubSecret(GITHUB_SECRET)
                        
                        // Additional deployment steps
                        sh "${VENV}/bin/python manage.py collectstatic --noinput"
                        sh "${VENV}/bin/python manage.py migrate"
                        // Additional deployment steps can be added as needed
                    }
                }
            }
        }
    }
}

