# Jenkins Setup Guide

## Prerequisites

- Jenkins 2.350+
- Java 11 or higher
- Git installed on Jenkins server
- Python 3.8+ for build environment

## Installation

### Step 1: Install Required Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Search for and install the following plugins:
   - Pipeline
   - GitHub
   - GitHub Integration
   - Cobertura Plugin
   - Email Extension Plugin
   - Log Parser Plugin

### Step 2: Add GitHub Credentials

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click **Add Credentials**
3. Fill in:
   - Kind: Username with password
   - Scope: Global
   - Username: `github-token`
   - Password: [Your GitHub Personal Access Token]
   - ID: `github-token`
4. Click **Create**

### Step 3: Configure GitHub Webhook

#### On GitHub Repository

1. Go to **Settings** → **Webhooks**
2. Click **Add webhook**
3. Configure:
   - Payload URL: `http://jenkins-server:8080/github-webhook/`
   - Content type: `application/json`
   - Events: Let me select individual events
     - ✓ Push events
     - ✓ Pull requests
   - Active: ✓
4. Click **Add webhook**

#### On Jenkins

1. Go to **Manage Jenkins** → **Configure System**
2. Find **GitHub** section
3. Add GitHub Server:
   - API URL: `https://api.github.com`
   - Credentials: Select `github-token`
   - Test connection

### Step 4: Create Pipeline Job

1. Click **New Item**
2. Name: `data-prepross-pipeline`
3. Type: **Pipeline**
4. Click **OK**

### Step 5: Configure Pipeline

#### General Settings
- **Description**: Data Preprocessing CI/CD Pipeline
- **GitHub project**: `https://github.com/230701393/data-prepross`

#### Build Triggers
- ✓ GitHub hook trigger for GITScm polling
- Build when a change is pushed to GitHub

#### Pipeline
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/230701393/data-prepross.git`
- Credentials: Select your GitHub credentials
- Branch Specifier: `*/main` `*/develop` `*/feature/*`
- Script Path: `Jenkinsfile`

### Step 6: Configure Post-Build Actions

#### Email Notifications

1. Add post-build action: **Editable Email Notification**
2. Configure:
   - Project Recipient List: `${BUILD_USER_EMAIL}`
   - Subject: `Build ${BUILD_NUMBER} - ${BUILD_STATUS}`
   - Body:
     ```
     Build Details:
     - Job: ${JOB_NAME}
     - Build: #${BUILD_NUMBER}
     - Status: ${BUILD_STATUS}
     - URL: ${BUILD_URL}
     ```

#### GitHub Status Updates

1. The Jenkinsfile already includes GitHub status notification
2. Verify credentials are configured correctly

### Step 7: Environment Variables

Set Jenkins environment variables:

1. Go to **Manage Jenkins** → **Configure System**
2. Global properties → Environment variables
3. Add:
   - `GITHUB_TOKEN`: [Your GitHub token]
   - `LOCAL_SERVER_PATH`: `/var/www/data-prepross`
   - `PYTHON_VERSION`: `3.9`
   - `COVERAGE_THRESHOLD`: `80`

## Jenkinsfile Overview

The pipeline includes these stages:

### 1. Checkout
- Clones repository
- Extracts branch, commit, and author information

### 2. Setup
- Verifies Python version
- Displays pip version

### 3. Install Dependencies
- Creates virtual environment
- Installs Python dependencies from requirements.txt

### 4. Code Quality - Lint
- Runs flake8 linting
- Generates JSON report
- Publishes HTML report

### 5. Code Formatting Check
- Runs black formatter check
- Warns if formatting issues found

### 6. Test
- Runs pytest with coverage
- Generates XML and HTML coverage reports
- Publishes JUnit test results

### 7. Coverage Analysis
- Checks coverage meets threshold (80%)
- Warns if below threshold

### 8. Build Artifacts
- Packages source files
- Creates tar.gz archive

### 9. Deploy to Staging (if develop branch)
- Deploys to `/var/www/data-prepross/staging`
- Restarts application on port 5000
- Performs health check

### 10. Deploy to Production (if main branch)
- Requires manual approval
- Deploys to `/var/www/data-prepross/production`
- Restarts application on port 5001
- Performs health check

### 11. Notify GitHub
- Updates commit status on GitHub
- Shows build result in PR

## Running a Build Manually

1. Go to the pipeline job
2. Click **Build Now**
3. Or click the dropdown and select **Build with Parameters**

## Monitoring Builds

### View Build Logs
1. Click on build number
2. Click **Console Output**
3. View real-time log stream

### Check Build Status
1. Go to job main page
2. See build history on left
3. Color indicators:
   - 🔵 Blue: Success
   - 🔴 Red: Failure
   - ⚫ Gray: Aborted

### Analyze Failures
1. Click on failed build
2. Review console output
3. Check specific stage where failure occurred
4. Review code changes in that commit

## Troubleshooting

### Build not triggering on push
```bash
# Check webhook on GitHub
# Go to Settings → Webhooks
# See Recent Deliveries tab
# Click on delivery to see response

# Test webhook manually
curl -X POST http://jenkins-server:8080/github-webhook/ \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main"}'
```

### Credential issues
```bash
# Verify GitHub token has correct permissions:
# - repo (full control of private repositories)
# - admin:repo_hook (write access to hooks)
# - read:org (read access to org settings)

# Test connection in Jenkins:
# Manage Jenkins → Configure System → GitHub
# Click "Test Connection"
```

### Virtual environment issues
```bash
# SSH into Jenkins server
ssh jenkins@jenkins-server

# Check Python installation
python3 --version

# Check pip
pip3 list

# Manually test venv creation
cd /tmp
python3 -m venv test-venv
source test-venv/bin/activate
pip install -r /path/to/requirements.txt
```

### Deployment failures
```bash
# Check target directory exists
ls -la /var/www/data-prepross

# Check application is running
ps aux | grep "python.*app.py"

# Check logs
tail -f /var/www/data-prepross/staging/app.log
tail -f /var/www/data-prepross/production/app.log

# Test health endpoint
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5001/health
```

## Useful Jenkins Commands

```bash
# SSH to Jenkins server
ssh jenkins@jenkins-server

# View Jenkins logs
tail -f /var/log/jenkins/jenkins.log

# Restart Jenkins
sudo systemctl restart jenkins

# Clear Jenkins cache
sudo rm -rf ~/.jenkins/workspace/*
```

## Performance Optimization

### Speed Up Builds

1. **Cache dependencies**:
   ```groovy
   // In Jenkinsfile
   options {
       skipDefaultCheckout()
       buildDiscarder(logRotator(numToKeepStr: '10'))
   }
   ```

2. **Use shallow clones**:
   ```groovy
   checkout([
       $class: 'GitSCM',
       branches: [[name: '*/main']],
       userRemoteConfigs: [[url: 'https://github.com/...']],
       extensions: [[$class: 'CloneOption', depth: 1]]
   ])
   ```

3. **Parallel stages**:
   ```groovy
   parallel {
       stage('Lint') { ... }
       stage('Test') { ... }
   }
   ```

## Backup and Recovery

### Backup Jenkins Configuration
```bash
# On Jenkins server
sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins/

# Copy to safe location
scp jenkins@jenkins-server:/home/jenkins/jenkins-backup.tar.gz .
```

### Restore Jenkins Configuration
```bash
# On Jenkins server
sudo systemctl stop jenkins
sudo tar -xzf jenkins-backup.tar.gz -C /
sudo systemctl start jenkins
```

## Security Best Practices

1. **Use personal access tokens** (not passwords)
2. **Limit token permissions** to only what's needed
3. **Rotate tokens regularly** (every 90 days)
4. **Encrypt secrets** in Jenkins credentials
5. **Audit webhook deliveries** regularly
6. **Use HTTPS** for webhook URLs
7. **Restrict Jenkins access** with firewall rules

## Next Steps

1. Verify all builds run successfully
2. Test GitHub webhook delivery
3. Monitor build logs for errors
4. Set up email notifications
5. Configure Slack integration
6. Set up metrics dashboard
