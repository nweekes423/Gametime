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
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/activate'
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py test game_monitor'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        withCredentials([string(credentialsId: 'Secret-ID', variable: 'GITHUB_SECRET')]) {
                            sh 'echo $GITHUB_SECRET'

                            if (params.ENVIRONMENT == 'main') {
                                sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py collectstatic --noinput'
                                sh '/Users/will/Gametime/nba_notifier/venv/bin/python manage.py migrate'
                            } else {
                                echo "Skipping production deployment steps for a non-production environment."
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to Elastic Beanstalk') {
            when {
                expression { params.ENVIRONMENT == 'dev' }
            }
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/pip install awsebcli'
                        sh 'venv/bin/eb use Github-Automation --region us-west-2'
                        sh 'venv/bin/eb deploy Github-Automation'
                    }
                }
            }
        }
    }
}