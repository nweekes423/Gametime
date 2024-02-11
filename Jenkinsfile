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
                    // Activate the virtual environment and install dependencies
                    sh 'source venv/bin/activate && pip install -r requirements.txt'
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
                        sh 'venv/bin/python manage.py collectstatic --noinput'
                        sh 'venv/bin/python manage.py migrate'
                        // Additional deployment steps can be added as needed
                    }
                }
            }
        }
    }
}
