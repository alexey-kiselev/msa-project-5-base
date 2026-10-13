.PHONY: up down minikube image apply job status

NS := analytics-export
IMAGE := shipments-export:local

# Build on host
UNSET_DOCKER := env -u DOCKER_HOST -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH -u MINIKUBE_ACTIVE_DOCKERD

up: minikube image apply job status

minikube:
	@if ! minikube status 2>/dev/null | grep -q "apiserver: Running"; then \
		minikube start --driver=docker --memory=3072 --cpus=2 --force; \
	fi
	@for i in $$(seq 1 60); do \
		if kubectl get nodes 2>/dev/null | grep -q ' Ready '; then \
			break; \
		fi; \
		sleep 2; \
	done
	kubectl get nodes

image:
	$(UNSET_DOCKER) docker buildx build --load -t $(IMAGE) ./app
	$(UNSET_DOCKER) minikube image load $(IMAGE)

apply:
	kubectl apply -f ./k8s/00-namespace.yaml
	kubectl apply -f ./k8s/01-postgres.yaml
	kubectl apply -f ./k8s/02-pvc.yaml
	kubectl apply -f ./k8s/03-cronjob.yaml
	@echo "Waiting for postgres..."
	kubectl -n $(NS) rollout status deployment/postgres --timeout=180s
	kubectl -n $(NS) wait --for=condition=ready pod -l app=postgres --timeout=180s

job:
	@echo "Triggerring Job from CronJob..."
	kubectl -n $(NS) delete job shipments-export-manual --ignore-not-found
	kubectl -n $(NS) create job shipments-export-manual --from=cronjob/shipments-export
	kubectl -n $(NS) wait --for=condition=complete job/shipments-export-manual --timeout=180s

status:
	@echo "Job status:"
	kubectl -n $(NS) get cronjob,job,pods
	@echo "Export logs:"
	mkdir -p ./status
	kubectl -n $(NS) get cronjob,job,pods -o wide | tee ./status/01-kubectl-status.txt
	kubectl -n $(NS) logs job/shipments-export-manual | tee ./status/02-job-logs.txt

down:
	kubectl delete namespace $(NS) --ignore-not-found
	minikube stop || true
	@echo "MiniKube stopped
	
delete:
	minikube delete || true
	@echo "MiniKube deleted"
