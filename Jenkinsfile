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
                    // Navigate to the project directory
                    dir('/Users/will/Gametime/nba_notifier') {
                        // Activate the virtual environment
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/activate'

                        // Use the full path to pip within the virtual environment
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Navigate to the project directory
                    dir('/Users/will/Gametime/nba_notifier') {
                        // Run the tests
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py test'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Navigate to the project directory
                    dir('/Users/will/Gametime/nba_notifier') {
                        // Use 'withCredentials' to securely access the GitHub secret
                        withCredentials([string(credentialsId: 'Secret-ID', variable: 'GITHUB_SECRET')]) {
                            // Example: Print the GitHub secret
                            sh 'echo $GITHUB_SECRET'
                            
                            // Additional deployment steps
                            sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py collectstatic --noinput'
                            sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py migrate'
                            // Additional deployment steps can be added as needed
                        }
                    }
                }
            }
        }
    }
}

