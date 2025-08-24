import jetbrains.buildServer.configs.kotlin.*
import jetbrains.buildServer.configs.kotlin.buildSteps.python
import jetbrains.buildServer.configs.kotlin.buildSteps.script
import jetbrains.buildServer.configs.kotlin.triggers.vcs
import jetbrains.buildServer.configs.kotlin.vcs.GitVcsRoot

version = "2023.11"

project {

    // Define VCS root - connects TeamCity to the GitHub repository
    vcsRoot(GitVcsRoot {
        id("PythonApp_GitVcsRoot")
        name = "Python App Repository"
        url = "https://github.com/timokito/pythonpasswordgenerator.git"
        branch = "refs/heads/main"
        branchSpec = "+:refs/heads/*"  // Monitor all branches
        authMethod = anonymous()         // Public repository, no auth needed
    })

    // Register build configurations
    buildType(Build)
    buildType(Test)
    buildType(DeployToRender)

    // Define build pipeline - each stage depends on the previous one
    sequential {
        buildType(Build)
        buildType(Test)
        buildType(DeployToRender)
    }
}

object Build : BuildType({
    id("PythonApp_Build")
    name = "Build"

    // Connect this build to the VCS root
    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        // Step 1: Install Python dependencies from requirements.txt
        script {
            name = "Install Dependencies"
            scriptContent = """
                pip install --upgrade pip        # Ensure pip is up to date
                pip install -r requirements.txt  # Install project dependencies
            """.trimIndent()
        }

        // Step 2: Compile Python files to check for syntax errors
        script {
            name = "Validate Syntax"
            scriptContent = """
                python -m py_compile app.py      # Compile main application file
                if [ -f test_app.py ]; then      # Check if test file exists
                    python -m py_compile test_app.py  # Compile test file
                fi
            """.trimIndent()
        }
    }

    // Automatically trigger build when code is pushed to main branch
    triggers {
        vcs {
            branchFilter = "+:main"
        }
    }
})

object Test : BuildType({
    id("PythonApp_Test")
    name = "Test"

    vcs {
        root(DslContext.settingsRoot)
    }

    // This stage runs only after Build completes successfully
    dependencies {
        snapshot(Build) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }

    steps {
        // Step 1: Execute unit tests using Python test runners
        python {
            name = "Run Tests"
            command = script {
                content = """
                    import subprocess
                    import sys
                    import os

                    # Check if test file exists before running tests
                    if not os.path.exists('test_app.py'):
                        print("No test file found, skipping tests")
                        sys.exit(0)  # Exit successfully if no tests

                    # Attempt to use pytest (preferred test runner)
                    try:
                        result = subprocess.run([sys.executable, "-m", "pytest", "test_app.py", "-v"],
                                              capture_output=True, text=True)
                    except:
                        # Fall back to unittest if pytest not available
                        result = subprocess.run([sys.executable, "-m", "unittest", "test_app.py"],
                                              capture_output=True, text=True)

                    # Output test results
                    print(result.stdout)
                    if result.returncode != 0:
                        print(result.stderr)
                        sys.exit(1)  # Fail the build if tests fail
                """.trimIndent()
            }
        }

        // Step 2: Check code quality using Python linter
        script {
            name = "Lint Check"
            scriptContent = """
                pip install flake8 --quiet                           # Install Python linter
                flake8 app.py --max-line-length=120 --ignore=E501 || true  # Run linter (non-blocking)
            """.trimIndent()
        }
    }

    // Set maximum execution time for test stage
    failureConditions {
        executionTimeoutMin = 5
    }
})

object DeployToRender : BuildType({
    id("PythonApp_DeployToRender")
    name = "Deploy to Render"

    vcs {
        root(DslContext.settingsRoot)
    }

    // This stage runs only after Test completes successfully
    dependencies {
        snapshot(Test) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }

    steps {
        // Step 1: Trigger deployment via Render.com webhook
        script {
            name = "Trigger Render Deployment"
            scriptContent = """
                # Call Render deploy hook using secure parameter (not visible in logs)
                response=${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Define parameter as password type to hide it in UI and logs
    params {
        password("env.RENDER_DEPLOY_HOOK", "",
                 label = "Render Deploy Hook",
                 description = "Render.com deployment webhook URL (stored securely)",
                 display = ParameterDisplay.HIDDEN)
    }
})}(curl -X POST \
                    -w "\nHTTP_STATUS:%{http_code}" \
                    -s \
                    "%env.RENDER_DEPLOY_HOOK%")

                # Extract HTTP status code from response
                http_status=${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}(echo "${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}response" | grep "HTTP_STATUS" | cut -d: -f2)
                # Extract response body (without exposing the URL)
                body=${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}(echo "${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}response" | grep -v "HTTP_STATUS")

                echo "Response: ${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}body"

                # Check if deployment was triggered successfully (2xx status codes)
                if [ "${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}http_status" -eq 200 ] || [ "${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}http_status" -eq 201 ] || [ "${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}http_status" -eq 202 ]; then
                    echo "✓ Deployment triggered successfully"
                    exit 0
                else
                    echo "✗ Deployment failed with status: ${'

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})}http_status"
                    exit 1  # Fail the build if deployment trigger fails
                fi
            """.trimIndent()
        }

        // Step 2: Brief wait and status message
        script {
            name = "Verify Deployment"
            scriptContent = """
                sleep 10  # Wait for deployment to initialize
                echo "Deployment triggered. Check Render dashboard for status."
            """.trimIndent()
        }
    }

    // Store deploy hook as parameter for easy configuration
    params {
        param("env.RENDER_DEPLOY_HOOK", "https://api.render.com/deploy/srv-d2k74c2li9vc73e11t5g?key=08HXHBhaTvQ")
    }
})