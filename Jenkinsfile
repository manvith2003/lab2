pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "manvith2003/wine-api"
    }

    stages {

        // ---------------- 1. Checkout ----------------
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ---------------- 2. Setup Python Virtual Environment ----------------
        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        // ---------------- 3. Train Model ----------------
        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python train.py
                '''
            }
        }

        // ---------------- 4. Read Accuracy ----------------
        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: 'outputs/results.json'
                    env.CURRENT_R2 = metrics.R2.toString()
                    echo "Current R2: ${env.CURRENT_R2}"
                }
            }
        }

        // ---------------- 5. Compare Accuracy ----------------
        stage('Compare Accuracy') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_R2')]) {

                        echo "Stored Best R2: ${BEST_R2}"

                        if (env.CURRENT_R2.toFloat() > BEST_R2.toFloat()) {
                            env.BUILD_IMAGE = "true"
                            echo "New model improved. Will build Docker image."
                        } else {
                            env.BUILD_IMAGE = "false"
                            echo "Model did not improve. Skipping Docker build."
                        }
                    }
                }
            }
        }

        // ---------------- 6. Build Docker Image ----------------
        stage('Build Docker Image') {
            when {
                expression { env.BUILD_IMAGE == "true" }
            }
            steps {
                sh "docker build -t $DOCKER_IMAGE:${BUILD_NUMBER} ."
                sh "docker tag $DOCKER_IMAGE:${BUILD_NUMBER} $DOCKER_IMAGE:latest"
            }
        }

        // ---------------- 7. Push Docker Image ----------------
        stage('Push Docker Image') {
            when {
                expression { env.BUILD_IMAGE == "true" }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_IMAGE:${BUILD_NUMBER}
                    docker push $DOCKER_IMAGE:latest
                    '''
                }
            }
        }
    }

    // ---------------- Artifact Archiving ----------------
    post {
        always {
            archiveArtifacts artifacts: 'outputs/**', fingerprint: true
        }
    }
}

