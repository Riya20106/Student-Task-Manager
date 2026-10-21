# Student Task Manager - CI/CD Pipeline (CCA 2)

CI/CD pipeline for an existing academic project, built with Jenkins, Docker, Docker Hub and Kubernetes (Minikube).

**Student:** Riya Sharma
**Course:** Cloud Computing and DevOps, TYCSE
**Repository:** https://github.com/Riya20106/Student-Task-Manager
**Docker Hub image:** `riyasharma06/student-task-manager`

## 1. Project

Student Task Manager is a small Flask web app where a student can view and add tasks. It has a `/health` endpoint, which Kubernetes uses to check that the app is alive. The project has 3 pytest tests (home page, add task, health endpoint) and runs in production with gunicorn on port 5000.

Repository layout:

- `app.py` - Flask application
- `templates/` and `static/` - HTML and static files
- `tests/` - pytest tests
- `requirements.txt` - Python dependencies
- `Dockerfile` - builds the container image
- `Jenkinsfile` - declarative pipeline
- `k8s/` - Kubernetes Deployment and Service files

## 2. Pipeline stages

The `Jenkinsfile` is a declarative pipeline with these stages:

| # | Stage | What it does |
|---|-------|--------------|
| 1 | Checkout | Jenkins pulls the latest code from the `main` branch on GitHub. |
| 2 | Install and Test | Creates a Python virtual environment, installs `requirements.txt` and runs `pytest`. The pipeline stops here if a test fails. |
| 3 | Build Docker Image | Runs `docker build` and tags the image with the Jenkins build number and `latest`. |
| 4 | Push Image to Docker Hub | Logs in to Docker Hub with credentials stored in Jenkins (ID `dockerhub-creds`) and pushes the image. |
| 5 | Deploy to Kubernetes | Runs `kubectl apply -f k8s/`, then `kubectl set image` with the new build-number tag and waits for the rollout to finish. |
| 6 | Verify Deployment | Prints the deployments, pods and services. |

The Docker Hub username and token are never written in the Jenkinsfile. They are stored as a "Username with password" credential in Jenkins.

## 3. Jenkins setup

Jenkins runs as a Docker container on my Windows laptop (Docker Desktop). *(Edit this section if you also set it up on an AWS EC2 instance.)*

1. Built a custom Jenkins image from `jenkins/jenkins` that adds the Docker CLI, Python 3 and `kubectl`.
2. Started the container with the Docker socket mounted (`-v /var/run/docker.sock:/var/run/docker.sock`) so pipeline stages can run `docker build` and `docker push` on the host's Docker engine. Jenkins data is kept in a Docker volume so jobs and credentials survive restarts.
3. Installed the suggested plugins (Pipeline, Git, Credentials, etc.).
4. Added a Docker Hub access token as a credential with ID `dockerhub-creds`.
5. Created a Pipeline job named `Student-Task-Manager-CI-CD` with **Pipeline script from SCM**, pointing at this GitHub repository, branch `main`, script path `Jenkinsfile`.
6. Connected the Jenkins container to the Minikube Docker network and gave `kubectl` inside Jenkins the Minikube cluster address and certificates, so the Deploy stage can reach the cluster.

## 4. Pushing the image

The Push stage logs in with the stored credential and pushes two tags:

- `riyasharma06/student-task-manager:<BUILD_NUMBER>` - one tag per Jenkins build
- `riyasharma06/student-task-manager:latest`

Kubernetes pulls the build-number tag from Docker Hub, so each deployment runs exactly the version that Jenkins built.

## 5. Deployment and access

Minikube runs with the Docker driver (`minikube start --driver=docker`). The `k8s/` folder has:

- `deployment.yaml` - Deployment `student-task-manager`, 1 replica, container port 5000, readiness and liveness probes on `/health`.
- `service.yaml` - Service `student-task-manager-service`, type NodePort (`80:30080`).

To open the app (the terminal must stay open on Windows with the Docker driver):

```
minikube service student-task-manager-service --url
```

Checks used to verify the deployment:

```
kubectl get pods
kubectl get deployments
kubectl get services
```

The pod shows `1/1 Running` and the app opens in the browser.

## 6. Second run (code change)

After the first successful run, I changed the page heading in `templates/index.html` to: **[Student Task Manager - Version 2]**. I committed and pushed the change to GitHub, then ran the pipeline again. Jenkins built a new image with the next build number, pushed it, and Kubernetes replaced the old pod with one running the new image. The new heading appeared in the browser.