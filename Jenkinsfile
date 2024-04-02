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
                            // Kill any existing process using port 8000
                            sh 'lsof -ti:8000 | xargs kill'
                            sh 'echo $GITHUB_SECRET'
                            sh 'source venv/bin/activate && python app/manage.py collectstatic --noinput'
                            sh 'source venv/bin/activate && python app/manage.py migrate'
                            sh 'source venv/bin/activate && python app/manage.py check'  
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

        stage('Test Docker Image') {
            steps {
                script {
                    // Run Docker container from the latest image, map container port 8001 to host port 8000
                    sh '/usr/local/bin/docker run -d -p 8000:8001 dockerrandy729/gametime:latest'

                    // Sleep for 10 seconds to give Docker container time to set up
                    sh 'sleep 20'

                    // Perform some basic tests on the running container
                    // For example, you can use curl to check if the web server responds
                    echo 'Testing web server with curl...'
                    sh 'curl https://localhost:8000 -k -vv'
                    echo 'Curl request completed.'
                }
            }
        }
    }
}

