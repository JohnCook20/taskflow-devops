// TaskFlow CI/CD pipeline (Declarative). Covers: Build, Test, Release, Deploy, Operate/Monitor checks.
// Requires on the Jenkins node: Docker, kubectl (or use the Ansible route in /ansible).
// Plugins: Pipeline, Docker Pipeline, JUnit, Cobertura/Coverage, Credentials Binding, GitHub.
pipeline {
  agent any

  environment {
    REGISTRY    = 'ghcr.io'
    IMAGE       = 'ghcr.io/YOUR_GITHUB_USER/taskflow'      // <-- change
    VERSION     = "1.0.${env.BUILD_NUMBER}"
    GIT_SHORT   = "${env.GIT_COMMIT?.take(7) ?: 'local'}"
    STAGING_URL = 'http://YOUR_STAGING_HOST:30080'         // <-- change
    PROD_URL    = 'http://YOUR_PROD_HOST:30080'            // <-- change
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 30, unit: 'MINUTES')
  }

  // Triggers: GitHub webhook (push) + cron safety net + nightly regression build.
  triggers {
    githubPush()                 // GitHub -> Settings -> Webhooks -> http://<jenkins>/github-webhook/
    pollSCM('H/5 * * * *')       // fallback if the webhook is missed
    cron('H 2 * * *')            // nightly scheduled build
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git log -1 --pretty=format:"%h %an %s"'
      }
    }

    stage('Lint') {
      agent { docker { image 'python:3.12-slim'; reuseNode true; args '-u root' } }
      steps {
        sh '''
          pip install --quiet -r requirements-dev.txt
          flake8 app tests
        '''
      }
    }

    stage('Unit Tests') {
      agent { docker { image 'python:3.12-slim'; reuseNode true; args '-u root' } }
      steps {
        sh '''
          pip install --quiet -r requirements-dev.txt
          mkdir -p reports
          pytest tests/test_api.py
        '''
      }
      post {
        always { junit 'reports/junit.xml' }
      }
    }

    stage('Build Image') {
      steps {
        sh 'docker build --build-arg APP_VERSION=${VERSION} -t ${IMAGE}:${VERSION} -t ${IMAGE}:latest .'
      }
    }

    stage('Integration Test') {
      steps {
        sh '''
          export APP_VERSION=${VERSION} APP_ENV=ci
          docker compose -p taskflow-ci up -d --build app
          scripts/smoke_test.sh http://localhost:5000 ${VERSION}
          docker run --rm --network host -e BASE_URL=http://localhost:5000 \
            -v "$PWD":/src -w /src python:3.12-slim \
            sh -c "pip install -q -r requirements-dev.txt && pytest tests/test_integration.py --no-cov"
        '''
      }
      post {
        always { sh 'docker compose -p taskflow-ci down -v || true' }
      }
    }

    stage('Release (push image)') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr-credentials',
                         usernameVariable: 'REG_USER', passwordVariable: 'REG_TOKEN')]) {
          sh '''
            echo "$REG_TOKEN" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
            docker push ${IMAGE}:${VERSION}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy to Staging') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-staging', variable: 'KUBECONFIG')]) {
          sh '''
            kubectl apply -k k8s/overlays/staging
            kubectl -n taskflow-staging set image deployment/taskflow taskflow=${IMAGE}:${VERSION}
            kubectl -n taskflow-staging rollout status deployment/taskflow --timeout=120s
          '''
        }
      }
    }

    stage('Staging Smoke Test') {
      when { branch 'main' }
      steps { sh 'scripts/smoke_test.sh ${STAGING_URL} ${VERSION}' }
    }

    stage('Approve Production') {
      when { branch 'main' }
      steps {
        timeout(time: 1, unit: 'HOURS') {
          input message: "Promote ${VERSION} to PRODUCTION?", ok: 'Deploy'
        }
      }
    }

    stage('Deploy to Production') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-production', variable: 'KUBECONFIG')]) {
          sh '''
            kubectl apply -k k8s/overlays/production
            kubectl -n taskflow-production set image deployment/taskflow taskflow=${IMAGE}:${VERSION}
            kubectl -n taskflow-production rollout status deployment/taskflow --timeout=180s
          '''
        }
        sh 'scripts/smoke_test.sh ${PROD_URL} ${VERSION}'
      }
    }
  }

  post {
    success { echo "Pipeline OK: ${IMAGE}:${VERSION}" }
    failure {
      echo 'Pipeline failed - rolling back production if a deploy was in flight.'
      withCredentials([file(credentialsId: 'kubeconfig-production', variable: 'KUBECONFIG')]) {
        sh 'kubectl -n taskflow-production rollout undo deployment/taskflow || true'
      }
    }
    always { cleanWs() }
  }
}
