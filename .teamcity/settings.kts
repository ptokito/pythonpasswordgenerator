import jetbrains.buildServer.configs.kotlin.*
import jetbrains.buildServer.configs.kotlin.buildFeatures.perfmon
import jetbrains.buildServer.configs.kotlin.buildSteps.python
import jetbrains.buildServer.configs.kotlin.buildSteps.script
import jetbrains.buildServer.configs.kotlin.triggers.vcs
import jetbrains.buildServer.configs.kotlin.vcs.GitVcsRoot

/*
 * Password Generator - Configuration as Code Demo
 * This demonstrates TeamCity's Kotlin DSL capabilities
 */

version = "2023.11"

project {
    description = "Password Generator with Configuration as Code"
    
    vcsRoot(GitHubVcsRoot)
    buildType(CI_CD_Pipeline)
    buildType(DeploymentPipeline)
    
    // Define build chain
    sequential {
        buildType(CI_CD_Pipeline)
        buildType(DeploymentPipeline, options = {
            onDependencyFailure = FailureAction.CANCEL
            onDependencyCancel = FailureAction.CANCEL
        })
    }
    
    params {
        password("env.RENDER_DEPLOY_HOOK", "credentialsJSON:render-deploy-hook", 
                 display = ParameterDisplay.HIDDEN,
                 description = "Render.com deployment webhook URL")
    }
}

object GitHubVcsRoot : GitVcsRoot({
    name = "Password Generator Repository"
    url = "https://github.com/ptokito/pythonpasswordgenerator"
    branch = "refs/heads/main"
    branchSpec = """
        +:refs/heads/*
        +:refs/pull/*/merge
    """.trimIndent()
    authMethod = anonymous()
})

object CI_CD_Pipeline : BuildType({
    name = "🔨 Build and Test"
    description = "Run tests and quality checks"
    
    artifactRules = """
        test-results.xml
        coverage.xml
        htmlcov => htmlcov.zip
    """.trimIndent()
    
    vcs {
        root(GitHubVcsRoot)
        cleanCheckout = true
    }
    
    steps {
        script {
            name = "📦 Install Dependencies"
            id = "install_deps"
            scriptContent = """
                #!/bin/bash
                echo "=== Setting up Python environment ==="
                python3 -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                echo "✅ Dependencies installed successfully"
            """.trimIndent()
        }
        
        python {
            name = "🧪 Run Unit Tests"
            id = "run_tests"
            command = pytest {
                scriptArguments = "test_app.py -v --junitxml=test-results.xml --cov=. --cov-report=xml --cov-report=html"
            }
        }
        
        script {
            name = "📊 Code Quality Analysis"
            id = "code_quality"
            scriptContent = """
                #!/bin/bash
                source venv/bin/activate
                pip install flake8 pylint black
                
                echo "=== Running code formatters and linters ==="
                black app.py --check || true
                flake8 app.py --max-line-length=120 || true
                pylint app.py --exit-zero
                
                echo "✅ Code quality analysis complete"
            """.trimIndent()
        }
        
        script {
            name = "🔍 Security Scan"
            id = "security_scan"
            scriptContent = """
                #!/bin/bash
                source venv/bin/activate
                pip install bandit safety
                
                echo "=== Running security scans ==="
                bandit -r app.py || true
                safety check || true
                
                echo "✅ Security scan complete"
            """.trimIndent()
        }
        
        script {
            name = "✅ Verify Application"
            id = "verify_app"
            scriptContent = """
                #!/bin/bash
                source venv/bin/activate
                
                echo "=== Starting application for smoke test ==="
                python app.py &
                APP_PID=$!
                sleep 5
                
                if curl -f http://localhost:5000/health; then
                    echo "✅ Application health check passed"
                    kill ${'$'}APP_PID
                    exit 0
                else
                    echo "❌ Application health check failed"
                    kill ${'$'}APP_PID
                    exit 1
                fi
            """.trimIndent()
        }
    }
    
    triggers {
        vcs {
            branchFilter = """
                +:main
                +:develop
                +:feature/*
            """.trimIndent()
        }
    }
    
    features {
        perfmon {
        }
        feature {
            type = "xml-report-plugin"
            param("xmlReportParsing.reportType", "junit")
            param("xmlReportParsing.reportDirs", "test-results.xml")
        }
    }
    
    requirements {
        contains("system.agent.os.family", "Linux")
    }
})

object DeploymentPipeline : BuildType({
    name = "🚀 Deploy to Production"
    description = "Deploy to Render.com hosting"
    
    vcs {
        root(GitHubVcsRoot)
    }
    
    steps {
        script {
            name = "📝 Pre-deployment Checks"
            scriptContent = """
                #!/bin/bash
                echo "=== Pre-deployment validation ==="
                echo "Branch: %teamcity.build.branch%"
                echo "Commit: %build.vcs.number%"
                echo "Build Number: %build.number%"
                
                if [ "%teamcity.build.branch%" != "main" ]; then
                    echo "⚠️ Warning: Deploying from non-main branch"
                fi
            """.trimIndent()
        }
        
        script {
            name = "🚀 Deploy to Render"
            scriptContent = """
                #!/bin/bash
                echo "=== Deploying to Render.com ==="
                
                if [ -z "%env.RENDER_DEPLOY_HOOK%" ]; then
                    echo "❌ RENDER_DEPLOY_HOOK not configured"
                    exit 1
                fi
                
                response=${'$'}(curl -X POST "%env.RENDER_DEPLOY_HOOK%" -w "\n%{http_code}" 2>/dev/null)
                http_code=${'$'}(echo "${'$'}response" | tail -n1)
                
                if [ "${'$'}http_code" = "200" ] || [ "${'$'}http_code" = "201" ]; then
                    echo "✅ Deployment triggered successfully"
                    echo "📱 Check Render dashboard for deployment status"
                else
                    echo "❌ Deployment failed with HTTP code: ${'$'}http_code"
                    exit 1
                fi
            """.trimIndent()
        }
        
        script {
            name = "🔔 Send Notifications"
            scriptContent = """
                #!/bin/bash
                echo "=== Sending deployment notifications ==="
                echo "✅ Deployment completed for build #%build.number%"
                # Add Slack/Email notification logic here
            """.trimIndent()
        }
    }
    
    dependencies {
        snapshot(CI_CD_Pipeline) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }
    
    requirements {
        contains("system.agent.os.family", "Linux")
    }
})
