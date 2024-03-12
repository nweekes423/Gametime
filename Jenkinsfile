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

        stage('Create Prod Environment') {
    when {
        expression { params.ENVIRONMENT == 'main' }
        script {
            def envExists = sh(
                script: "aws elasticbeanstalk describe-environments --environment-names Github-Automation-Prod --region us-west-2 --query 'Environments' --output text",
                returnStatus: true
            ) == 0
            if (!envExists) {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/pip install awsebcli'
                        sh 'venv/bin/eb create Github-Automation-Prod --region us-west-2'
                    }
                }
            }
        }
    }
}

        stage('Deploy to Elastic Beanstalk') {
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh '/Users/will/Gametime/nba_notifier/venv/bin/pip install awsebcli'

                        if (params.ENVIRONMENT == 'dev') {
                            sh 'venv/bin/eb use Github-Automation --region us-west-2'
                            sh 'venv/bin/eb deploy Github-Automation'
                        } else if (params.ENVIRONMENT == 'main') {
                            sh 'venv/bin/eb use Github-Automation-Prod --region us-west-2'
                            sh 'venv/bin/eb deploy Github-Automation-Prod'
                        }
                    }
                }
            }
        }
    }
}