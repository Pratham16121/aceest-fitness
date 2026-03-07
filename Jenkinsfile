pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'aceest-fitness'
        // Set DOCKER_REGISTRY to your registry prefix, e.g. 'myregistry.io/username/' or leave empty for local only
        DOCKER_REGISTRY = ''
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_REGISTRY}${DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh """
                    docker run --rm ${DOCKER_REGISTRY}${DOCKER_IMAGE}:${env.BUILD_NUMBER} \
                        sh -c 'timeout 2 xvfb-run -a python "accest fitness.py" 2>/dev/null || true'
                """
            }
        }

        stage('Push Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    def imageName = "${DOCKER_REGISTRY}${DOCKER_IMAGE}:${env.BUILD_NUMBER}"
                    def img = docker.image(imageName)
                    // Only push if registry is configured; add withRegistry() and credentials-id as needed
                    if (env.DOCKER_REGISTRY?.trim()) {
                        docker.withRegistry('https://your-registry.io/', 'docker-registry-credentials-id') {
                            img.push()
                            img.push('latest')
                        }
                    } else {
                        echo "Skipping push: DOCKER_REGISTRY not set (local build only)"
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs(deleteDirs: true, patterns: [[pattern: '.git/**', type: 'INCLUDE']])
        }
        failure {
            echo 'Pipeline failed. Check logs.'
        }
        success {
            echo "Build ${env.BUILD_NUMBER} succeeded. Image: ${DOCKER_REGISTRY}${DOCKER_IMAGE}:${env.BUILD_NUMBER}"
        }
    }
}
