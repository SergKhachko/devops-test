# Export temp creds
export AWS_ACCESS_KEY_ID=****
export AWS_SECRET_ACCESS_KEY=****
export AWS_DEFAULT_REGION=eu-west-1

# Run EC2 instance with appropriate AMI, etc
aws ec2 run-instances \
    --image-id ami-0a90581127c6c8677 \
    --security-group-ids sg-0d712d9df362c2213 \
    --count 1 \
    --instance-type t2.medium \
    --key-name devops-test \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=skhachko}]' \
    --region eu-west-1

# Find the intstance ID by tag
aws ec2 describe-instances \
    --region eu-west-1 \
    --filters "Name=tag:Name,Values=skhachko" \
    --query "Reservations[*].Instances[*].[InstanceId,State.Name,Tags]"

# Get instance IP by instance ID
aws ec2 describe-instances \
    --instance-ids i-0eed22c08e4ba605d \
    --query 'Reservations[*].Instances[*].PublicIpAddress' \
    --output text

# Prepare key permissions
chmod 400 devops-test.pem
ssh -i devops-test.pem ec2-user@18.201.129.232

# Prepare workdir
mkdir -p ~/task && cd task

# Get repo
sudo yum install git
git clone https://github.com/adimentech/devops-test.git && cd devops-test

# Prepare docker image (use /deploy/kustomization.yaml as a reference to a desired git tag)
docker login -u serhiikhachko -p ****
docker build -t serhiikhachko/test-task .
docker tag serhiikhachko/test-task:latest serhiikhachko/test-task:v1
docker push serhiikhachko/test-task:latest
docker push serhiikhachko/test-task:v1

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install mysql (take node tolerations into account)
helm install mysql bitnami/mysql --set primary.tolerations[0].key=system,primary.tolerations[0].operator=Exists,primary.tolerations[0].effect=NoSchedule --set auth.rootPassword=B8QaP4x2

# Install kustomize
cd ~/task
curl -L -o kustomize.tar.gz "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.3.0/kustomize_v5.3.0_linux_amd64.tar.gz"
tar xzf kustomize.tar.gz
sudo mv kustomize /usr/local/bin/

# Apply manifests (fix tollerations and image)
cd ~/task/devops-test/
kustomize build deploy/ | kubectl apply -f -

# Check task
kubectl exec -it devops-test-cc84c799d-tsd2j -- sh
curl devops-test:8000/get-node
{"message":"You've get response from node minikube-test"}

# Permissions task
kubectl api-resources -o wide # determine available resource types
