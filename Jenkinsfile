pipeline {
    agent any

    // Run the pipeline every weekday at 08:30 (Mon–Fri only)
    triggers {
        cron("30 8 * * 1-5")
    }

    // Keep last 10 builds and add timestamps to logs
    options {
        buildDiscarder(logRotator(numToKeepStr: "10"))
        timestamps()
    }

    stages {
        // Clean old data
        stage("Clean Old Data") {
            steps {
                sh '''
                    echo "🧹 Cleaning old data..."
                    rm -f data/sources/*.json
                    rm -f data/staging/*.csv
                    rm -f data/warehouse/*.csv
                    rm -f logs/*.log
                '''
            }
        }

        // Build fresh Docker image for all tests
        stage("Build Test Container Image") {
            steps {
                sh '''
                    echo "🔧 Building test images..."
                    docker compose build test
                '''
            }
        }

        // Build fresh Docker image for App
        stage("Build App Container Image") {
            steps {
                sh '''
                    echo "🔧 Building app image..."
                    docker compose build app
                '''
            }
        }

        //Check ENV file
        stage("Check ENV file") {
            steps {
                sh '''
                    if [ -f .env ]; then
                        echo "📄 .env file found: Configuration values will be loaded from this file."
                        cat .env
                    else
                        echo "⚠️  .env file not found. Continuing with default values."
                    fi
                '''
            }
        }

        // Check the file structure before running the pipeline
        stage("Initial File Check") {
            steps {
                sh '''
                    echo "File structure BEFORE pipeline"
                    ls -ltr data
                    ls -ltr logs
                '''
            }
        }

        // Run Unit Tests
        stage("Run Unit Tests") {
            steps {
                sh '''
                    echo "🧪 Running UNIT tests..."
                    docker compose run --rm -e TEST_TYPE=unit test
                '''
            }
        }

        // Run Integration tests
        stage("Run Integration Tests") {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                sh '''
                    echo "🧪 Running INTEGRATION tests..."
                    docker compose run --rm -e TEST_TYPE=integration test
                '''
            }
        }

        // Run Main Pipeline
        stage("Run Main Pipeline") {
            steps {
                sh '''
                    docker compose run app
                '''
            }
        }

        // Check the file structure after the pipeline
        stage("Final File Check") {
            steps {
                sh '''
                    echo "File structure AFTER pipeline"
                    ls -ltr data
                    ls -ltr logs
                '''
            }
        }

        // Basic build metadata
        stage("Build Info") {
            steps {
                sh '''
                    echo "Job Name     : $JOB_NAME"
                    echo "Build ID     : $BUILD_ID"
                    echo "Build URL    : $BUILD_URL"
                    echo "Running on   : $NODE_NAME"
                    echo "Workspace    : $WORKSPACE"
                    echo "Triggered at : $(date '+%A %d %B %Y - %H:%M')"
                '''
            }
        }

    }

    // Messages
    post {
        success {
            echo "Pipeline completed successfully!"
            archiveArtifacts artifacts: 'data/**/*, logs/**/*', allowEmptyArchive: true
        }
        failure {
            echo "Pipeline failed."
        }
    }
}
