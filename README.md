# Student Task Manager — CI/CD College Project

A small Flask web application used to demonstrate a CI/CD workflow with GitHub, Jenkins, Docker, Docker Hub, and Kubernetes.

## What the app does

- Shows two sample study tasks.
- Adds a task.
- Marks a task complete/incomplete.
- Deletes a task.
- Shows total, completed, and remaining counts.
- Provides `/health` for a simple health check.

**Demo limitation:** tasks are stored in the browser's Flask session cookie, not in a database. They are for demonstration and are not shared between browsers or users. Use a strong `FLASK_SECRET_KEY` for a real deployment.

## Project files

- `app.py` — Flask routes and application logic.
- `templates/index.html` — webpage structure.
- `static/style.css` — visual styling.
- `tests/test_app.py` — automated tests.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — instructions for packaging the app as a container image.
- `Jenkinsfile` — automated pipeline stages.
- `k8s/deployment.yaml` — tells Kubernetes which container to run.
- `k8s/service.yaml` — makes the application reachable through a Kubernetes Service.
- `.gitignore`, `.dockerignore` — exclude local and unnecessary files.

## 1. Run locally on Windows

Install Python 3.12 or newer and Git. Open this folder in VS Code, then choose **Terminal → New Terminal** (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Press `Ctrl+C` in the terminal to stop it.

If PowerShell blocks activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Test with Docker locally (optional)

Install and start Docker Desktop first. From the project folder:

```powershell
docker build -t student-task-manager:local .
docker run --rm -p 5000:5000 student-task-manager:local
```

Open `http://localhost:5000`. Stop the container with `Ctrl+C`.

## 3. One-time setup needed for full CI/CD

The automated pipeline needs these services to be installed and connected. These are setup tasks, not commands you should have to type at every presentation.

1. **GitHub:** create a repository and push this project.
2. **Docker Hub:** create a repository named `student-task-manager`. Replace `YOUR_DOCKERHUB_USERNAME` in `Jenkinsfile` and `k8s/deployment.yaml` with your actual username.
3. **Jenkins:** install Jenkins on a Linux machine/EC2 instance, then install the suggested plugins.
4. **Jenkins credential:** add a **Username with password** credential with ID `dockerhub-creds`. Use your Docker Hub username and a Docker Hub access token as the password. Do not put the token in this repository.
5. **Docker access:** Jenkins must be allowed to run Docker commands.
6. **Kubernetes:** install and start a cluster such as Minikube, and configure `kubectl` so it works as the same Linux user that runs Jenkins.
7. **Jenkins job:** create a Pipeline job configured as **Pipeline script from SCM**, select Git, enter the GitHub repository URL, set branch `*/main`, and set script path to `Jenkinsfile`.

The Jenkins Linux user must be able to run `python3`, `git`, `docker`, and `kubectl`, and must have access to the Kubernetes cluster. The sample pipeline assumes these tools are installed and configured. Exact setup commands depend on whether you use a local machine or EC2.

## 4. What happens when you click Build Now

1. **Checkout:** Jenkins downloads the latest code from GitHub.
2. **Install and Test:** installs Python dependencies and runs `pytest`.
3. **Build Docker Image:** creates a versioned container image.
4. **Push Image to Docker Hub:** uploads the versioned image and the `latest` tag.
5. **Deploy to Kubernetes:** applies the Kubernetes YAML files and updates the Deployment to the new build image.
6. **Verify Deployment:** prints Deployment, Pod, and Service status.

A successful run should show all stages green and the Deployment rollout completed. If a stage fails, open that build and select **Console Output** to see the error.

## 5. Access the Kubernetes app

On the machine configured for the cluster, check:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

For Minikube, try:

```bash
minikube service student-task-manager-service --url
```

If Kubernetes is running on an EC2 host with Minikube, one demo option is to run this on the EC2 host:

```bash
kubectl port-forward --address 0.0.0.0 service/student-task-manager-service 8081:80
```

Then allow inbound TCP port `8081` in the EC2 security group **from your own public IP only**, and open `http://EC2_PUBLIC_IP:8081`. Keep SSH restricted to your IP. Do not expose Jenkins or other admin ports publicly. Stop port-forwarding after the demo. Network configuration can vary by Minikube driver.

## 6. Professor demonstration plan

1. Open the app and add a task.
2. Mark it complete and show the counts changing.
3. Open GitHub and show `app.py`, `Dockerfile`, `Jenkinsfile`, and `k8s/`.
4. Open Jenkins and show the pipeline stages from the latest successful build.
5. Open that build's Console Output and point out the test results, image push, and rollout verification.
6. Show the Docker Hub image tags.
7. Run `kubectl get pods`, `kubectl get deployments`, and `kubectl get services`.
8. Make a tiny visible change, such as changing the page subtitle in `templates/index.html`, commit and push it, then click **Build Now** in Jenkins.
9. After the pipeline succeeds, refresh the app and show the updated subtitle. This demonstrates the continuous deployment loop.

## Common issues

- **Tests fail locally:** run `python -m pytest -q` and read the first traceback.
- **Docker command fails:** make sure Docker Desktop is running locally, or Docker Engine is running on the Jenkins host.
- **Jenkins cannot find Docker/kubectl:** install the tools and check permissions and PATH for the Jenkins service user.
- **Docker Hub login/push fails:** verify the credential ID is exactly `dockerhub-creds`, and use a Docker Hub access token.
- **ImagePullBackOff:** confirm the image name is correct and the repository is public, or configure an image pull secret for a private repository.
- **kubectl connection refused:** make sure the Kubernetes cluster is running and the Jenkins user has the correct kubeconfig/context.
- **Pod is not ready:** use `kubectl describe pod POD_NAME` and `kubectl logs POD_NAME`.

## Important

This is a teaching/demo project, not a production system. Do not commit access tokens, passwords, SSH private keys, or secret configuration to GitHub. Cloud services may incur charges; stop or delete resources you no longer need.
