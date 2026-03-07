# Jenkins, Docker & CI/CD Setup – ACEest Fitness

This project includes Docker and a Jenkins pipeline for build, test, and (optional) push.

## Quick start with Docker

**Build the image:**
```bash
docker build -t aceest-fitness .
```

**Run (headless with virtual display):**
```bash
docker run --rm aceest-fitness xvfb-run -a python "accest fitness.py"
```

**Run with Docker Compose:**
```bash
docker compose up --build
```

---

## 1. Docker setup

- **Install Docker:** [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)
- **Install Docker Compose v2:** Usually included with Docker Desktop; or `pip install docker-compose` / use the standalone binary.

**Verify:**
```bash
docker --version
docker compose version
```

---

## 2. Jenkins setup

### 2.1 Install Jenkins

**macOS (Homebrew):**
```bash
brew install jenkins-lts
brew services start jenkins-lts
```

**Linux (generic):**
```bash
# Example: Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
echo "deb https://pkg.jenkins.io/debian binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list
sudo apt update && sudo apt install -y jenkins
sudo systemctl start jenkins
```

**Docker (run Jenkins in Docker):**
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
# Get initial admin password: docker exec <container_id> cat /var/jenkins_home/secrets/initialAdminPassword
```

Open **http://localhost:8080**, complete the wizard, and install suggested plugins.

### 2.2 Plugins required for this pipeline

In **Manage Jenkins → Manage Plugins → Available**:

- **Docker Pipeline**
- **Pipeline** (often already installed)
- **Git** (for checkout)

Install and restart Jenkins if prompted.

### 2.3 Docker inside Jenkins

Jenkins must be able to run `docker` (build and run images).

- **If Jenkins runs on the host:** Install Docker on the same machine and add the Jenkins user to the `docker` group:  
  `sudo usermod -aG docker jenkins` (Linux) and restart Jenkins.
- **If Jenkins runs in Docker:** Run Jenkins with Docker socket and CLI, e.g.:
  ```bash
  docker run -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
  ```
  And install Docker inside the Jenkins container, or use a Jenkins agent that has Docker.

### 2.4 Create the pipeline job

1. **New Item** → name (e.g. `aceest-fitness`) → **Pipeline** → OK.
2. **Pipeline** section:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** your repo URL (e.g. `https://github.com/your-org/aceest-fitness.git`)
   - **Credentials:** add if private repo
   - **Branch:** `*/main` or `*/master`
   - **Script Path:** `Jenkinsfile`
3. Save, then **Build Now**.

---

## 3. CI/CD workflow (Jenkinsfile)

The pipeline does:

| Stage         | Action |
|----------------|--------|
| Checkout       | Clone the repo |
| Build Docker   | `docker build` → image `aceest-fitness:<BUILD_NUMBER>` |
| Smoke Test     | Run container headless with `xvfb-run` and timeout to verify app starts |
| Push Image     | Only on `main`/`master`; runs only if you configure a registry (see below) |

### 3.1 Pushing to a Docker registry

To push images from Jenkins:

1. **Set registry in the job (or in Jenkinsfile):**  
   In the job’s **Environment** or in the Jenkinsfile, set:
   - `DOCKER_REGISTRY` = your prefix, e.g. `myregistry.io/username/`

2. **Add registry credentials in Jenkins:**  
   **Manage Jenkins → Credentials** → Add **Username and password** (or “Docker Hub” / “Secret text” as needed). Note the **Credentials ID**.

3. **Use that ID in the Jenkinsfile:**  
   In the `Push Image` stage, replace:
   - `https://your-registry.io/` with your registry URL.
   - `docker-registry-credentials-id` with the ID from step 2.

Example for Docker Hub:
- `DOCKER_REGISTRY = 'docker.io/youruser/'`
- Registry URL: `https://index.docker.io/v2/`
- Credentials: Docker Hub username + password or access token.

---

## 4. File overview

| File / folder      | Purpose |
|--------------------|--------|
| `Dockerfile`       | Builds the app image (Python + Tkinter + xvfb). |
| `docker-compose.yml` | Run the app via `docker compose up`. |
| `Jenkinsfile`      | Pipeline: checkout → build → smoke test → optional push. |
| `.dockerignore`    | Keeps build context small. |
| `requirements.txt` | Python deps (Tkinter is stdlib; optional for future deps). |

---

## 5. Optional: run GUI on your machine (no Docker)

```bash
python3 "accest fitness.py"
```

On minimal Linux installs you may need: `sudo apt install python3-tk` (or equivalent).

---

## 6. Troubleshooting

- **Jenkins “docker: command not found”**  
  Ensure the Jenkins process (or agent) can run `docker` (PATH, docker group, or Docker-in-Docker setup).

- **Smoke test fails**  
  Check that the image has `xvfb-run` and `timeout` (the Dockerfile includes them). Inspect the Jenkins console log for the exact `docker run` command and error.

- **Push fails**  
  Confirm `DOCKER_REGISTRY` and the registry URL/credentials in the Jenkinsfile match your registry. Use “Pipeline Syntax” → “withRegistry” to generate snippet if needed.

- **Permission denied (Docker socket)**  
  On Linux, add the Jenkins user to the `docker` group and restart Jenkins.

If you tell me your OS (e.g. macOS/Linux) and where Jenkins runs (host vs Docker), I can tailor the exact commands and job config for you.
