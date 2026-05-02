# DevOps EKS Project

This project demonstrates:
- AWS EKS
- Terraform
- Kubernetes
- Docker
- CI/CD

Architecture diagram coming soon.# aws-eks-project

-------STEPS--------
1. Clone repo to your local environment
2. Create Docker images for relavant apps 
   Example : for user-service app --->  Run this code in user-service folder location - docker build -t user-service:v1 .
3. Create ECR Repositories
   Go to AWS Console → ECR
   Create 3 repos: 
                  1. user-service
                  2. order-service
                  3. api-gateway
4. LOGIN TO ECR
   Run this command in cli - aws configure
   Then - aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com   
   example : aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 191798899170.dkr.ecr.us-east-1.amazonaws.com
5. TAG & PUSH IMAGES
   For USER-SERVICE - docker tag user-service:v1 <ECR_URL>/user-service:v1 (example : docker tag user-service:v1 191798899170.dkr.ecr.us-east-1.amazonaws.com/user-service:v1 )
                      docker push <ECR_URL>/user-service:v1 ( example : docker push 191798899170.dkr.ecr.us-east-1.amazonaws.com/user-service:v1)
   For ORDER-SERVICE - docker tag order-service:v1 <ECR_URL>/order-service:v1
                      docker push <ECR_URL>/order-service:v1
   For API-GATEWAY - docker tag api-gateway:v1 <ECR_URL>/api-gateway:v1
                      docker push <ECR_URL>/api-gateway:v1

TERRAFORM + EKS (STEP-BY-STEP)
1. Go to the terraform folder
2. Run below commands : 
   terraform init
   terraform plan
   terraform apply 
if you want delete all you can run this command :  terraform destroy
3. CONNECT TO EKS
   Configure kubectl  -  aws eks update-kubeconfig \
--region us-east-1 \
--name devops-eks-cluster
4. Test
   Check pods - kubectl get pods -A
   Check services - kubectl get svc
DEPLOY MICROSERVICES TO EKS + ALB
1.Add IAM OIDC provider (already in Terraform enable_irsa = true)
  aws eks describe-cluster --name devops-eks-cluster --region us-east-1 \
--query "cluster.identity.oidc.issuer" --output text
2.Install Helm (if not installed)
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
3.Add AWS LB Controller repo
  helm repo add eks https://aws.github.io/eks-charts
  helm repo update
4.Install AWS Load Balancer Controller
  CREATE IAM POLICY 
  Download policy  - curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
  Create policy    - aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json
  Create IAM Role for Controller - 
  eksctl create iamserviceaccount \
  --cluster devops-eks-cluster \
  --namespace kube-system \
  --name aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve
  Install controller
  helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=devops-eks-cluster \
  --set serviceAccount.create=false \
  --set region=us-east-1 \
  --set vpcId=<YOUR_VPC_ID> \
  --set serviceAccount.name=aws-load-balancer-controller
5.Create a namespace for your project
  kubectl create namespace devops-app
6.KUBERNETES DEPLOYMENTS (for user-service, order-service, api-gateway)
  USER SERVICE DEPLOYMENT - k8s/user-service.yaml
# k8s/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: devops-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user
          image: <ECR_URL>/user-service:v1
          ports:
            - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: devops-app
spec:
  selector:
    app: user-service
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP

ORDER SERVICE : k8s/order-service.yaml
# k8s/order-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: devops-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order
          image: <ECR_URL>/order-service:v1
          ports:
            - containerPort: 5001
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: devops-app
spec:
  selector:
    app: order-service
  ports:
    - port: 80
      targetPort: 5001
  type: ClusterIP

API GATEWAY : k8s/api-gateway.yaml
# k8s/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: devops-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api-gateway
          image: <ECR_URL>/api-gateway:v1
          ports:
            - containerPort: 5002
          env:
            - name: USER_SERVICE_URL
              value: http://user-service.devops-app.svc.cluster.local
            - name: ORDER_SERVICE_URL
              value: http://order-service.devops-app.svc.cluster.local
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: devops-app
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 5002
  type: NodePort

INGRESS (ALB) - k8s/ingress.yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: devops-ingress
  namespace: devops-app
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
    - http:
        paths:
          - path: /*
            pathType: ImplementationSpecific
            backend:
              service:
                name: api-gateway
                port:
                  number: 80

7.APPLY TO CLUSTER
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/order-service.yaml
kubectl apply -f k8s/api-gateway.yaml
kubectl apply -f k8s/ingress.yaml

8.VERIFY
kubectl get pods -n devops-app
kubectl get svc -n devops-app
kubectl get ingress -n devops-app
**You should see an ALB DNS. Open it in browser: http://<ALB_DNS>/dashboard/1
You should see:

{
  "user": {"id":1,"name":"Alice"},
  "orders": [{"id":1,"item":"Laptop","user_id":1}]
}
****
8.SCALING & HIGH AVAILABILITY
kubectl scale deployment user-service --replicas=4 -n devops-app
kubectl scale deployment api-gateway --replicas=3 -n devops-app
9.MONITORING
kubectl top pod -n devops-app

CI/CD PIPELINE (FULL PRODUCTION SETUP)
