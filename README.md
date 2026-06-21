# ShopStack — Kubernetes + Helm + ArgoCD GitOps Demo Platform

ShopStack is a demo e-commerce-style platform built to **learn and demonstrate production-style application deployment on Kubernetes** using **Helm** and **ArgoCD GitOps**.

The project combines:

* a **FastAPI backend**
* a **static frontend served by Nginx**
* **PostgreSQL** for persistent product storage
* **Redis** for caching
* a reusable **Helm chart**
* **ArgoCD** for GitOps-based deployment from GitHub to Kubernetes

The main goal of this project was to learn Kubernetes, Helm, and GitOps by deploying a **multi-service application end-to-end**, instead of studying isolated YAML examples.

---

# 1. Project Motivation

I built ShopStack to get hands-on experience with the full deployment lifecycle of a containerized application:

* package application components into Docker images
* deploy stateless and stateful workloads on Kubernetes
* manage configuration using ConfigMaps and Secrets
* package the application using Helm
* manage desired state through Git and ArgoCD
* debug real operational issues such as PVC binding problems, missing secrets, startup ordering, and deployment reconciliation

Instead of treating Kubernetes as only a theory topic, this project was used as a practical platform to understand how application deployment, state management, and GitOps workflows fit together.

---

# 2. Architecture Overview

## 2.1 Application Architecture

```text
Browser
   ↓
Frontend Service → Frontend Pod(s) (Nginx)
   ↓
Backend Service → Backend Pod(s) (FastAPI)
   ├─ PostgreSQL Service → PostgreSQL StatefulSet + PVC
   └─ Redis Service → Redis Deployment
```

## 2.2 Deployment / Delivery Architecture

```text
GitHub repository
   └─ Helm chart + values files
        ↓
ArgoCD Application
        ↓
Kubernetes cluster
        ↓
ShopStack resources in namespace
```

ArgoCD watches the Git repository and continuously reconciles the Kubernetes cluster to match the desired state defined in Git.

---

# 3. Tech Stack

## Application

* **Backend:** FastAPI
* **Frontend:** HTML / CSS / JavaScript served by Nginx
* **Database:** PostgreSQL
* **Cache:** Redis

## Platform / DevOps

* **Containers:** Docker
* **Orchestration:** Kubernetes
* **Packaging:** Helm
* **GitOps:** ArgoCD

---

# 4. Features

## 4.1 Application Features

* Product list API backed by PostgreSQL
* Product creation API
* Redis-backed caching for product retrieval
* Backend health endpoint for readiness / liveness checks

## 4.2 Kubernetes / Platform Features

* Backend, frontend, and Redis deployed using **Deployments**
* PostgreSQL deployed using **StatefulSet** with **PersistentVolumeClaim**
* Internal service-to-service communication using **Kubernetes Services**
* Backend configuration managed through **ConfigMap**
* Sensitive values managed through **Secrets**
* Optional **Ingress** support
* **Readiness** and **Liveness** probes
* **CPU / memory requests and limits**
* Separate **dev** and **prod** Helm values files

## 4.3 GitOps Features

* ShopStack deployed through an **ArgoCD Application**
* ArgoCD watches GitHub and syncs cluster state from Git
* Git-driven configuration / scaling changes are reconciled into the cluster
* Backend chart supports checksum-based rollout on ConfigMap / Secret changes

---

# 5. Repository Structure

```text
shopstack-k8s-gitops/
├─ app/
│  ├─ backend/
│  │  ├─ Dockerfile
│  │  ├─ main.py
│  │  └─ requirements.txt
│  └─ frontend/
│     ├─ Dockerfile
│     ├─ index.html
│     ├─ app.js
│     ├─ styles.css
│     └─ nginx.conf
│
├─ k8s/
│  └─ base/
│     ├─ backend/
│     ├─ frontend/
│     ├─ postgres/
│     ├─ redis/
│     ├─ config/
│     ├─ secret/
│     ├─ ingress/
│     └─ namespace/
│
├─ helm/
│  └─ shopstack/
│     ├─ Chart.yaml
│     ├─ values.yaml
│     ├─ values-dev.yaml
│     ├─ values-prod.yaml
│     └─ templates/
│
├─ gitops/
│  └─ argocd/
│     └─ shopstack-dev-application.yaml
│
├─ .github/
│  └─ workflows/
│     └─ ci.yaml
│
└─ README.md
```

---

# 6. Kubernetes Resources Used

ShopStack uses the following Kubernetes resource types:

* **Namespace** — application isolation
* **Deployment** — backend, frontend, Redis
* **StatefulSet** — PostgreSQL
* **Service** — internal networking and stable DNS
* **PersistentVolumeClaim (PVC)** — PostgreSQL storage
* **ConfigMap** — backend non-secret configuration
* **Secret** — backend and PostgreSQL sensitive values
* **Ingress** — optional external routing
* **Readiness / Liveness probes**
* **Resource requests / limits**

---

# 7. Helm Chart Design

The reusable Helm chart lives in:

```text
helm/shopstack
```

## 7.1 Values Files

* `values.yaml` → common default values
* `values-dev.yaml` → development overrides
* `values-prod.yaml` → production-style overrides

## 7.2 Helm Chart Capabilities

* reusable labels / selectors via `_helpers.tpl`
* configurable replicas
* configurable image pull policy
* configurable ingress enable / disable
* configurable resource requests / limits
* configurable readiness / liveness probes
* checksum-based rollout support for backend ConfigMap / Secret changes

---

# 8. GitOps with ArgoCD

ArgoCD is used to deploy and reconcile ShopStack from GitHub.

## 8.1 ArgoCD Application Configuration

The ShopStack ArgoCD Application points to:

* **Repository:** this GitHub repository
* **Path:** `helm/shopstack`
* **Values file:** `values-dev.yaml`

## 8.2 GitOps Workflow

1. Change Helm values or templates in Git
2. Commit and push to GitHub
3. ArgoCD detects the desired-state change
4. ArgoCD syncs the Kubernetes cluster to match Git

This project demonstrates a GitOps deployment model where **Git is the source of truth** for the Kubernetes environment.

---

# 9. How to Run

## 9.1 Prerequisites

Before running ShopStack, make sure you have:

* Docker
* Kubernetes cluster (Docker Desktop / Minikube / Kind, etc.)
* `kubectl`
* `helm`
* optional: ArgoCD for GitOps deployment

---

## 9.2 Build Container Images

### Backend

```bash
cd app/backend
docker build -t shopstack-backend:v1 .
```

### Frontend

```bash
cd app/frontend
docker build -t shopstack-frontend:v1 .
```

If you are using a local Kubernetes cluster such as Docker Desktop, make sure the cluster can access the locally built images, or push them to a registry if needed.

---

## 9.3 Deploy with Helm

From the repository root:

```bash
helm lint ./helm/shopstack
helm upgrade --install shopstack-dev ./helm/shopstack -f helm/shopstack/values-dev.yaml
```

Check resources:

```bash
kubectl get pods -n shopstack-helm
kubectl get svc -n shopstack-helm
```

---

## 9.4 Access the Backend

Example port-forward:

```bash
kubectl port-forward svc/shopstack-backend-service 8001:8000 -n shopstack-helm
```

Then test:

```bash
curl http://localhost:8001/api/health
curl http://localhost:8001/api/products
```

---

## 9.5 Deploy with ArgoCD

1. Install ArgoCD in the cluster
2. Apply the ArgoCD Application manifest:

```bash
kubectl apply -f gitops/argocd/shopstack-dev-application.yaml
```

3. ArgoCD will deploy ShopStack from the Helm chart in this repository

---

# 10. CI Workflow

The repository includes a GitHub Actions workflow:

```text
.github/workflows/ci.yaml
```

The CI pipeline performs:

* **Helm lint** on the ShopStack chart
* **Helm template render** using development values
* **basic backend Python validation** using `py_compile`

This gives quick feedback if a push breaks the chart or introduces obvious backend syntax issues.

---

# 11. Key Learning Outcomes

This project was built as a practical Kubernetes + Helm + GitOps learning platform.
Key areas covered:

## Kubernetes

* difference between stateless and stateful workloads
* when to use Deployments vs StatefulSets
* internal service discovery with Services
* persistent storage using PVCs
* health checks using readiness/liveness probes
* resource requests and limits

## Helm

* packaging Kubernetes manifests into a reusable chart
* separating common values from environment-specific overrides
* reducing duplication using helpers
* debugging chart issues such as PVC / Secret naming mismatches

## GitOps / ArgoCD

* using Git as the source of truth
* deploying a Helm chart via an ArgoCD Application
* reconciling cluster state from Git
* validating Git-driven scaling and deployment updates

## Debugging / Operations

During development, the project involved debugging real Kubernetes / Helm issues such as:

* `Pending` pods caused by PVC naming / binding problems
* `CreateContainerConfigError` caused by missing Secrets
* backend startup timing and database initialization issues
* handover from manual Helm deployment to ArgoCD-managed deployment

---

# 12. Example Operational Scenarios Covered

While building ShopStack, the following operational scenarios were handled:

* backend deployment failing because PostgreSQL Secret was missing
* PostgreSQL pod remaining Pending because PVC was misnamed or not yet bound
* backend service failing until database initialization logic was added
* Redis cache integration and cache invalidation on product creation
* migration from manual Helm deployment to ArgoCD GitOps management
* Git-driven scaling changes reconciled automatically into the cluster

These are exactly the kinds of problems that helped turn the project from “toy YAML” into a more realistic platform exercise.

---

# 13. Future Improvements

Possible next improvements:

* add update / delete product APIs
* introduce DB migration tooling such as Alembic
* add automated backend test coverage
* extend observability with Prometheus / Grafana / Loki
* add Horizontal Pod Autoscaler (HPA)
* add production-grade ingress / TLS setup
* add stricter environment separation for dev / prod deployment workflows

---

# 14. Why This Project Matters

ShopStack is not just a CRUD app deployed to Kubernetes.
The project is valuable because it demonstrates the **full lifecycle** of a platform-style application:

* application containers
* stateful + stateless workload deployment
* internal networking and service discovery
* persistent storage
* configuration and secret management
* Helm packaging
* GitOps deployment with ArgoCD
* debugging and reconciliation of real operational issues

That combination makes it a strong hands-on learning project for:

* **Backend / Platform / DevOps interviews**
* Kubernetes / Helm / GitOps portfolio work
* understanding how application code and deployment infrastructure connect in practice

---

# 15. GitHub Repository

Repository URL:

https://github.com/thisisratnesh/shopstack-k8s-gitops
