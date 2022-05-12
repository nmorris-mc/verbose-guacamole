node('docker') {
  def tasks = [:]

  checkoutRepo()
  // BWH :TRICKY: 2021-01-24 Added these lines because the diff quality and
  // coverage reports had stopped working. Apparently "origin/main" branch
  // is no longer available inside the Docker container.
  sh "git checkout main"
  sh "git checkout HEAD@{1}"


  // Only run these checks on pull requests, not commit events/branches
  // https://confluence.mailchimp.com/display/EN/Jenkinsfiles#Jenkinsfiles-ManagingyourJenkinsfileacrossbothbranchesandPRs
  if (isPR()) {
    tasks["App tests and quality checks"] = {
      stage('Python tests') {
        def gitManager = new rsg.GitHubManager();
        withDocker() {
          sh 'docker-compose build'
          // Uncomment the code below (and the end brace below) when you need to
          // connect to GCP as part of test runs. Add a new Jenkins credential at
          // https://jenkins.rsglab.com/credentials/ and then add the credential ID below.
          // More info here:
          // https://confluence.mailchimp.com/display/DS/Setting+up+a+Jenkins+build+to+use+GCP+Credentials
          //withCredentials([file(credentialsId: '<<JENKINS CREDENTIALS KEY NAME>>', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
            // Create docker-compose.jenkins.yml which sets up a mounted directory
            // so the GOOGLE_APPLICATION_CREDENTIALS file is available inside the
            // container.
            sh 'script/create_jenkins_docker_compose_config.sh'
            try {
              // The "-p" option ensures container names do not collide across
              // builds.
              sh 'docker-compose -f docker-compose.yml -f docker-compose.jenkins.yml -p {{cookiecutter.package_name}}_tests_3_$BRANCH_NAME$BUILD_NUMBER run --entrypoint script/dockerci app'
              gitManager.passCheck("Python 3 testing", currentBuild.absoluteUrl, "./script/dockerci passed")
              sh 'docker-compose -f docker-compose.yml -f docker-compose.jenkins.yml -p {{cookiecutter.package_name}}_tests_3_$BRANCH_NAME$BUILD_NUMBER down -v'
            }
            catch(e) {
              error(e.message)
              sh 'docker-compose -f docker-compose.yml -f docker-compose.jenkins.yml -p {{cookiecutter.package_name}}_tests_3_$BRANCH_NAME$BUILD_NUMBER down -v'
              gitManager.failCheck("Python 3 testing", currentBuild.absoluteUrl, "./script/dockerci failed: ${e}")
            }
          //}
        }
      }
    }
  }

  parallel tasks

  // Attempt to publish the latest build automatically
  if (isRunningOnRepo('rsg/{{cookiecutter.package_name}}') && env.BRANCH_NAME == 'main') {
    withCredentials([[
      $class: "UsernamePasswordMultiBinding",
      credentialsId: "artifactory",
      usernameVariable: "ARTIFACTORY_USERNAME",
      passwordVariable: "ARTIFACTORY_TOKEN"
    ],
    // Uncomment the code below when you need to connect to GCP as part of building
    // a Python package (probably as part of download_package_data.py). Add a new
    // Jenkins credential at https://jenkins.rsglab.com/credentials/ and then add
    // the credential ID below. More info here:
    // https://confluence.mailchimp.com/display/DS/Setting+up+a+Jenkins+build+to+use+GCP+Credentials

    //file(credentialsId: 'jenkins-credential-id', variable: 'GOOGLE_APPLICATION_CREDENTIALS')
    ]) {
      stage("Publish Python Library") {
        try {
          withDocker {
            sh 'docker-compose build'
            // Ensure that Docker can write to file in shared volume. script/python-publish.sh
            // below will write to this file indicating the outcome of uploading the package.
            sh 'chmod 777 .twine_output/twine-exit'
            sh 'script/create_jenkins_docker_compose_config.sh'
            try {
              sh '''docker-compose \
              -f docker-compose.yml -f docker-compose.jenkins.yml \
              -p {{cookiecutter.package_name}}_py_pkg_pub_$BRANCH_NAME$BUILD_NUMBER \
              run -e ARTIFACTORY_USERNAME -e ARTIFACTORY_TOKEN -e BUILD_NUMBER \
              --entrypoint script/python-publish.sh app'''
              def twine_exit_status = readFile(file: '.twine_output/twine-exit').trim()
              def version_num = sh(
                script: 'sed -n -e "s/^version\\s*=\\s*//p" setup.cfg',
                returnStdout: true
              ).trim()
              if (twine_exit_status == "already_exists"){
                message = """Last merged PR for {{cookiecutter.package_name}} Python
library did not increment version. <${env.RUN_DISPLAY_URL}|Build link> :nothingtodohere:"""
                sendSlackMessage("#a-ds-blinken-lights", message, "good")
              } else if (twine_exit_status == "published"){
                message = """Python library {{cookiecutter.package_name}} version ${version_num}
is now available! <${env.RUN_DISPLAY_URL}|Build link> :party-blob2:"""
                sendSlackMessage("#a-ds-blinken-lights", message, "good")
              } else {
                message = """Failed to release new version of the {{cookiecutter.package_name}}
Python library. <${env.RUN_DISPLAY_URL}|Build link> :siren:"""
                sendSlackMessage("#a-ds-blinken-lights", message, "danger")
              }
              sh 'docker-compose -f docker-compose.yml -f docker-compose.jenkins.yml -p {{cookiecutter.package_name}}_py_pkg_pub_$BRANCH_NAME$BUILD_NUMBER down -v'
            }
            catch(e) {
              error(e.message)
              sh 'docker-compose -f docker-compose.yml -f docker-compose.jenkins.yml -p {{cookiecutter.package_name}}_py_pkg_pub_$BRANCH_NAME$BUILD_NUMBER down -v'
              message = """Failed to release new version of the {{cookiecutter.package_name}}
Python library. <${env.RUN_DISPLAY_URL}|Build link> :siren:"""
              sendSlackMessage("#a-ds-blinken-lights", message, "danger")
            }
          }
        } catch (e) {
          message = """Failed to release new version of the {{cookiecutter.package_name}}
Python library. <${env.RUN_DISPLAY_URL}|Build link> :siren:"""
          sendSlackMessage("#a-ds-blinken-lights", message, "danger")
        }
      }
    }
  }
}
