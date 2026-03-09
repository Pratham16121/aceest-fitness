pipeline {
    agent any

    environment {
        IMAGE = "prathamgoel16/aceest"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                sh "docker build -t ${IMAGE}:${BUILD_NUMBER} ."
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                sh """
                docker push ${IMAGE}:${BUILD_NUMBER}
                docker tag ${IMAGE}:${BUILD_NUMBER} ${IMAGE}:latest
                docker push ${IMAGE}:latest
                """
            }
        }

    }
}