pipeline {
    agent any

    parameters {
        choice(
            choices: ['dev', 'main'],
            description: 'Select the environment',
            name: 'ENVIRONMENT'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    dir('/Users/will/Gametime') {
                        sh 'source venv/bin/activate && pip install -r app/nba_notifier/requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('/Users/will/Gametime') {
                        sh 'source venv/bin/activate && python app/manage.py test game_monitor'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    dir('/Users/will/Gametime') {
                        withCredentials([string(credentialsId: 'Secret-ID', variable: 'GITHUB_SECRET')]) {
                            sh 'echo $GITHUB_SECRET'

                            if (params.ENVIRONMENT == 'main') {
                                sh 'source venv/bin/activate && python app/manage.py collectstatic --noinput'
                                sh 'source venv/bin/activate && python app/manage.py migrate'
                            } else {
                                echo "Skipping production deployment steps for a non-production environment."
                            }
                        }
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Build Docker image
                    sh '/usr/local/bin/docker build -t my-django-app /Users/will/Gametime'
                    
                    // Tag and push Docker image
                    sh '/usr/local/bin/docker tag my-django-app dockerrandy729/gametime:latest'
                    sh '/usr/local/bin/docker push dockerrandy729/gametime:latest'
                }
            }
        }
    }
}
