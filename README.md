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
2. Create Docker images for relavant app 
   Example : for user-service app --->  Run this code in user-service folder location - docker build -t api-gateway:v1 .
3. Create ECR Repositories
   Go to AWS Console → ECR
   Create 3 repos: 
                  1. user-service
                  2. order-service
                  3. api-gateway
4. LOGIN TO ECR
   Run this command in cli - aws configure
   Then - aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com   
5. TAG & PUSH IMAGES
   For USER-SERVICE - docker tag user-service:v1 <ECR_URL>/user-service:v1
                      docker push <ECR_URL>/user-service:v1
   For ORDER-SERVICE - docker tag order-service:v1 <ECR_URL>/order-service:v1
                      docker push <ECR_URL>/order-service:v1
   For API-GATEWAY - docker tag api-gateway:v1 <ECR_URL>/api-gateway:v1
                      docker push <ECR_URL>/api-gateway:v1