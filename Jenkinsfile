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



        stage('Push to Docker Hub') {
            steps {
                script {
              		dir('/Users/will/Gametime') {
                		sh 'source nba_notifier/venv/bin/activate && /usr/local/bin/docker build -t dockerrandy729/gametime:latest .'
                		sh 'source nba_notifier/venv/bin/activate && /usr/local/bin/docker push dockerrandy729/gametime:latest'
            	}
                }
            }
        }
    }
}