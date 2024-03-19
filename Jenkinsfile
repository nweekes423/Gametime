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
                        sh 'source venv/bin/activate && pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh 'source venv/bin/activate && python manage.py test game_monitor'
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
                                sh 'source venv/bin/activate && python manage.py collectstatic --noinput'
                                sh 'source venv/bin/activate && python manage.py migrate'
                            } else {
                                echo "Skipping production deployment steps for a non-production environment."
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
                        sh 'source venv/bin/activate && pip install awsebcli'

                        if (params.ENVIRONMENT == 'dev') {
                            sh 'source venv/bin/activate && eb use Github-Automation --region us-west-2'
                            sh 'source venv/bin/activate && eb deploy Github-Automation'
                        } else if (params.ENVIRONMENT == 'main') {
                            sh 'source venv/bin/activate && eb use Github-Automation-Prod --region us-west-2'
                            sh 'source venv/bin/activate && eb deploy Github-Automation-Prod'
                        }
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    dir('/Users/will/Gametime/nba_notifier') {
                        sh 'source venv/bin/activate && /usr/local/bin/docker tag my-django-app dockerrandy729/gametime:latest'
                        sh 'source venv/bin/activate && /usr/local/bin/docker push dockerrandy729/gametime:latest'
                    }
                }
            }
        }
    }
}
