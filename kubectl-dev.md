# connect to prometheus

```
kubectl port-forward -n monitoring deploy/prometheus-server 9090
```

connect to:

http://localhost:9090

## login to pod

kubectl get pods -n dev
kubectl exec -it budget-web-app-c4874449d-kdw8v -n dev -- /bin/sh
kubectl exec -it budget-api-app-5d9f9dc8b9-gxjdt -n dev -- /bin/sh

## get logs

##tail -f on all pods

```
for pod in $(kubectl get pods -n dev -o jsonpath='{.items[*].metadata.name}'); do
  kubectl logs -f $pod -n dev &
done
wait

```

## list services

kubectl get services -n dev
kubectl get pods -n dev

kubectl describe pod budget-web-app -n dev
kubectl describe pod budget-ai-app -n dev
kubectl describe pod budget-api-app -n dev

kubectl logs -f budget-api-app-5d9689f479-wvbsh -n dev

kubectl logs -l app=budget-web-app -n dev --tail=100
kubectl logs -l app=budget-api-app -n dev --tail=100

kubectl logs -l app=budget-ai-app -n dev --tail=100

```
## stop web


## stop all pods
kubectl -n dev scale deployment budget-web-app --replicas=0
## start again
kubectl -n dev scale deployment budget-web-app --replicas=1
## restart dev

```

kubectl -n dev rollout restart deployment budget-web-app
kubectl -n dev rollout restart deployment budget-api-app
kubectl -n dev rollout restart deployment budget-ai-app

-- stop dev

```

## kubernetes events

```

kubectl describe pod budget-ai-app -n dev

```

# re-apply dev config

```

kubectl apply -f ./kube/config/dev

```

# getting dev config

```

kubectl get configmap budget-web-dev-config -n dev -o yaml

```

# deploying dev secrets

```

kubectl delete secret budget-web-dev-secrets -n dev
kubectl delete secret budget-api-dev-secrets -n dev
kubectl delete secret budget-ai-dev-secrets -n dev

kubectl create secret generic budget-web-dev-secrets \
--from-env-file=.dev-web-secrets.env \
--namespace=dev

kubectl create secret generic budget-api-dev-secrets \
--from-env-file=.dev-api-secrets.env \
--namespace=dev

kubectl create secret generic budget-ai-dev-secrets \
--from-env-file=.dev-ai-secrets.env \
--namespace=dev

kubectl create secret generic mathapi-secrets \
--from-env-file=.dev-mathapi-secrets.env \
--namespace=dev

```

# get all secrets

```

kubectl get secret budget-api-dev-secrets -n dev -o yaml

```

# get pariticular decoded secret

## eg mongodb

```

kubectl get secret budget-web-dev-secrets -n dev -o jsonpath="{.data.MONGODB_URI}" | base64 --decode
kubectl get secret budget-web-dev-secrets -n dev -o jsonpath="{.data.AUTH0_CLIENT_SECRET}" | base64 --decode

```

```

The Prometheus PushGateway can be accessed via port 9091 on the following DNS name from within your cluster:
prometheus-prometheus-pushgateway.monitoring.svc.cluster.local

Get the PushGateway URL by running these commands in the same shell:

```
  export POD_NAME=$(kubectl get pods --namespace monitoring -l "app=prometheus-pushgateway,component=pushgateway" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace monitoring port-forward $POD_NAME 9091
```

# Create secrets for mathapi
kubectl create secret generic mathapi-secrets \
--from-env-file=.dev-mathapi-secrets.env \
--namespace=dev
