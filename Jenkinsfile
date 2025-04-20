// CI pipeline for weather forecast ETL workflow, containerized with Docker Compose

pipeline {
    agent any

    // Select resampling interval (used in cleaning step)
    parameters {
        choice(
            name: "INTERVAL",
            choices: ["30min", "20min", "15min", "10min"],
            description: "Resampling interval for the cleaned forecast data"
        )
    }

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
                    rm -f data/raw/*.json
                    rm -f data/cleaned/*.csv
                    rm -f data/cleaned/*.parquet
                    rm -f logs/*.log
                    rm -f config/*.json
                '''
            }
        }

        // Build fresh Docker image
        stage("Build Test Container Image") {
            steps {
                sh '''
                    echo "🔧 Building test image..."
                    docker compose build test
                '''
            }
        }

        //Check APIKEY
        stage("Check API Key") {
            steps {
                sh 'cat .env || echo ".env not found!"'
            }
        }

        // Check the file structure before running the pipeline
        stage("Initial File Check") {
            steps {
                sh '''
                    echo "File structure BEFORE pipeline"
                    ls -ltr data
                    ls -ltr logs
                    ls -ltr config
                '''
            }
        }

        // Pytest
        stage("Run Pytest") {
            steps {
                sh '''
                    echo "Running unit tests with pytest..."
                    docker compose run --rm test
                '''
            }
        }

        // Step 1
        stage("Step 1: Get IP Info") {
            steps {
                sh '''
                    docker compose run ip
                '''
            }
        }

        // Step 2
        stage("Step 2: Fetch Weather Data") {
            steps {
                sh '''
                    docker compose run weather
                '''
            }
        }

        // Step 3
        stage("Step 3: Clean Forecast Data") {
            steps {
                sh '''
                    docker compose run cleaning
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
                    ls -ltr config
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
