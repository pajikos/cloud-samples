---
title: "Azure Functions in Kubernetes Example"
date: "2022-03-31"
categories: 
  - "azure"
tags: 
  - "cloud"
  - "azure"
  - "functions"
  - "keda"
  - "service-bus"
---
## Introduction
This tutorial shows how to deploy two simple examples of Azure Functions written in Python to Kubernetes (AKS used here, but not required).

## Envrironment setup
### Install prerequisites
* Docker (e.g. https://www.docker.com/products/docker-desktop)
* Kubectl (https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* Azure cli (https://docs.microsoft.com/cs-cz/cli/azure/install-azure-cli)
* Func cli (https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)

### Download Functions source code
```bash
git clone git@github.com:pajikos/cloud-samples.git
cd cloud-samples/azure-functions-in-k8s
```

### Setup your custom properties
Edit file `.env` and fill correct values.

### Load envrironment properties
```bash
# Load env properties
source .env
```
### Login to the Docker registry
You need a Docker registry with push rights to be able to upload images with two functions.
You have to be logged, here is an example when using Azure Container Registry:
```bash
# Auth with AAD accounts
az acr login -n $ACR_NAME
```

### Deploy KEDA to cluster
For more info, visit: https://keda.sh/docs/2.6/deploy/
Please note, that you do not need Keda version 2.2 and above(required for Durable Functions only).

#### Create namespace for Keda
```bash
# Create namespace
kubectl create namespace keda
```

There are two ways how to deploy KEDA:
* Install Keda using Azure Func Core Tools
```bash
# Deploy keda
func kubernetes install --namespace keda
```
* Install Keda using the official Helm chart
```bash
# Add Helm repo
helm repo add kedacore https://kedacore.github.io/charts
#Update Helm repo
helm repo update
# Create namespace
kubectl create namespace keda
#Install keda Helm chart
helm install keda kedacore/keda --namespace keda
```

## Deploying Azure Functions (non-durable function)
This example shows how to deploy two functions to the AKS cluster:
* Simple HTTP Trigger-based function - return response to HTTP GET imediately.
* ServiceBus trigger-based function - automatic scaling based on the number of messages in a queue, simply consuming messages and logging them to console


### Setup ServiceBus Namespace
One of the functions uses Azure Service Bus, so here is the tutorial on how to create it using az cli:
```bash
az servicebus namespace create --resource-group $RG --name $SERVICEBUS_NAMESPACE --location $LOC --sku Standard

az servicebus queue create --name $QUEUE_NAME \
    --resource-group $RG \
    --namespace-name $SERVICEBUS_NAMESPACE

az servicebus queue authorization-rule create --resource-group $RG --namespace-name $SERVICEBUS_NAMESPACE --queue-name $QUEUE_NAME --name $POLICY_NAME --rights Listen Send Manage
PRIMARY_KEY=$(az servicebus queue authorization-rule keys list --resource-group $RG --namespace-name $SERVICEBUS_NAMESPACE --queue-name queue-input --name $POLICY_NAME --query primaryKey --output tsv)   
# Assign env property with connection strings to queue
export ServiceBusConnectionString="Endpoint=sb://$SERVICEBUS_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=$POLICY_NAME;SharedAccessKey=$PRIMARY_KEY;"
# Keda needs Connection string including entity path (i.e. the full path)
export ServiceBusConnectionStringQueue="Endpoint=sb://$SERVICEBUS_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=$POLICY_NAME;SharedAccessKey=$PRIMARY_KEY;EntityPath=$QUEUE_NAME"
# Run the following lines and insert the output to local.settings.json 
echo "\"ServiceBusConnectionStringQueue\": \"$ServiceBusConnectionStringQueue\""
echo "\"ServiceBusConnectionString\": \"$ServiceBusConnectionString\""


# Optional, Getting root access key (= global access to the whole namespace)
ROOT_CONNECTION_STRING=$(az servicebus namespace authorization-rule keys list --resource-group $RG --namespace-name $SERVICEBUS_NAMESPACE --name RootManageSharedAccessKey --query primaryConnectionString --output tsv)
```

### Test local run
If the Azure Service Bus and queue successfully installed, you can run functions locally:
```bash
cd simple_function_demo
func start
```
If no problem, successful output:
```console
[azure-functions-in-k8s/simple_function_demo]func start
Found Python version 3.9.10 (python3).

Azure Functions Core Tools
Core Tools Version:       4.0.3971 Commit hash: d0775d487c93ebd49e9c1166d5c3c01f3c76eaaf  (64-bit)
Function Runtime Version: 4.0.1.16815

...

Functions:

  HttpTriggerTest: [GET,POST] http://localhost:7071/api/HttpTriggerTest

  ServiceBusQueueTrigger: serviceBusTrigger
```

### Building and deploying the testing function
If run local properly, we can now deploy functions to AKS.
```bash
FUNCTION_NAME=k8sfntest
FUNCTION_NS_NAME=functions-test
func kubernetes deploy --name $FUNCTION_NAME --min-replicas 0 --max-replicas 5 --cooldown-period 30 --image-name $ACR_NAME.azurecr.io/functiontestdeploy:latest --namespace $FUNCTION_NS_NAME -i --dry-run > deployment.yaml
```
The following steps are needed:
1. Open deployment.yaml for editing
2. Find definition of ScaledObject (k8sfntest) and replace: ServiceBusConnectionString -> ServiceBusConnectionStringQueueInput (Kuda Azure ServiceBus integration needs full queue endpoint.)

```bash
# Create namespace
kubectl create namespace $FUNCTION_NS_NAME
# Run deployment
kubectl apply -f deployment.yaml -n $FUNCTION_NS_NAME
```

### Setting access to deployed app
A new service during deployment was created, so here you can extract its external service IP.
```bash
# list all running services
kubectl get services --namespace $FUNCTION_NS_NAME
# Save service IP to variable
SERVICE_IP=$(k get svc $FUNCTION_NAME-http --namespace $FUNCTION_NS_NAME -o jsonpath='{.status.loadBalancer.ingress[*].ip}')
```

Go to:
```bash
echo "Invoke url: http://$SERVICE_IP/api/httptriggertest?name=Pavel"
```

### Test consuming messages from the queue
To send a batch of messages to the Azure Service Bus namespace, you can do it on Azure Portal or simply use my Python script.
Install script dependencies first:
```bash
pip install azure.servicebus
```
In the Azure Service Bus section of this page, a connection string was exported as an environment variable, so you can now run the script directly:
```bash
python send_message.py
```
Successful output:
```console
Sent a list of 100 messages
Sent a batch of 100 messages
Done sending messages
-----------------------
```
## Clean resources
```bash
kubectl delete namespace $FUNCTION_NS_NAME
```

## Resources
* https://docs.microsoft.com/en-us/azure/azure-functions/functions-kubernetes-keda
* https://docs.microsoft.com/en-us/azure/azure-functions/functions-core-tools-reference?tabs=v2#func-kubernetes-deploy
* https://www.wesleyhaakman.org/scaling-azure-functions-from-zero-to-n-hero-on-kubernetes-with-keda/
* https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-queues

