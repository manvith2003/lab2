pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "manvith24/wine-api"
        BUILD_DOCKER = "false"
    }

    stages {
        stage('Checkout') {
            steps {
                // Clone the GitHub repository (handled automatically by SCM config)
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    apt-get update && apt-get install -y python3-venv python3-pip
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_ACCURACY = metrics.accuracy.toString()
                    echo "Current Model Accuracy (R2 Score): ${env.CURRENT_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACCURACY')]) {
                    script {
                        echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                        echo "Best Accuracy:    ${BEST_ACCURACY}"

                        if (env.CURRENT_ACCURACY.toDouble() > BEST_ACCURACY.toDouble()) {
                            echo "New model is BETTER! Proceeding to build and push Docker image."
                            env.BUILD_DOCKER = "true"
                        } else {
                            echo "New model did NOT improve. Skipping Docker build and push."
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.BUILD_DOCKER == "true" }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest .
                    """
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.BUILD_DOCKER == "true" }
            }
            steps {
                sh """
                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', allowEmptyArchive: true
            echo 'Pipeline execution completed.'
        }
        success {
            echo 'Pipeline finished successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}
