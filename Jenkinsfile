// Set TRAFFICGEN_BASE_URL, TRAFFICGEN_USER and TRAFFICGEN_PASS (all 'Secret text') as Jenkins credentials.
// Without a base URL only the offline unit tests run.
pipeline {
    agent any

    environment {
        TRAFFICGEN_BASE_URL = credentials('TRAFFICGEN_BASE_URL')
        TRAFFICGEN_USER     = credentials('TRAFFICGEN_USER')
        TRAFFICGEN_PASS     = credentials('TRAFFICGEN_PASS')
    }

    stages {
        stage('Install') {
            steps {
                sh 'python3 -m venv .venv'
                sh '. .venv/bin/activate && pip install -r tests/requirements.txt -r robot/requirements.txt'
            }
        }

        stage('Unit tests (offline)') {
            steps {
                sh '. .venv/bin/activate && pytest tests/ -v -k "not smoke_live" --junitxml=results/pytest-unit.xml'
            }
        }

        stage('Smoke tests (live appliance)') {
            when { expression { return env.TRAFFICGEN_BASE_URL?.trim() } }
            steps {
                sh '. .venv/bin/activate && pytest tests/test_smoke_live.py -v --junitxml=results/pytest-smoke.xml'
            }
        }

        stage('Robot Framework') {
            when { expression { return env.TRAFFICGEN_BASE_URL?.trim() } }
            steps {
                sh '. .venv/bin/activate && robot --outputdir results/robot robot/example.robot'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'results/*.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'results/**'
        }
    }
}
