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
                        sh 'source venv/bin/activate && python app/manage.py test game_monitor --exclude=test_views.py'
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
                            sh 'source venv/bin/activate && python app/manage.py collectstatic --noinput'
                            sh 'source venv/bin/activate && python app/manage.py migrate'
                            sh 'source venv/bin/activate && python app/manage.py check'  

                            // Stop the existing container

                            // Start the new container
                            sh "export PATH=/usr/local/bin:\$PATH && docker-compose up --build -d"

                            
                        }
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    // Authenticate with Docker Hub using credentials
                    withCredentials([usernamePassword(credentialsId: '67925980-58ae-4262-bd41-d178efedad93', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '/usr/local/bin/docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    }

                    // Tag and push Docker image
                    sh '/usr/local/bin/docker tag gametime-django dockerrandy729/gametime:latest'
                    sh '/usr/local/bin/docker push dockerrandy729/gametime:latest'
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    // Run Docker container from the latest image, map container port 8000 to a different host port, e.g., 8080
                    // Starting the services again to ensure they are running for testing
                    
                    // Sleep for 20 seconds to give Docker container time to set up
                    sh 'sleep 20'

                    // Perform some basic tests on the running container
                    // For example, you can use curl to check if the web server responds
                    echo 'Testing web server with curl...'
                    sh 'curl -kL  http://localhost'
                    echo 'Curl request completed.'
                }
            }
        }
    }
}

