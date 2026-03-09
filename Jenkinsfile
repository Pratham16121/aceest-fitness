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

        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }

        stage('Build Image') {
            steps {
                sh "docker build -t ${IMAGE}:${BUILD_NUMBER} ."
            }
        }

        stage('Docker Login') {
            steps {
                sh 'echo dckr_pat_gmlv5MdeqzIIJh9xfOqTaNDk92s | docker login -u prathamgoel16 --password-stdin'
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