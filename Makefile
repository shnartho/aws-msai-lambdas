# Build the Lambda function package
build:
build:
	@echo "Building Lambda function package..."
	powershell -Command "cd lambdas/msai-image-uploader; if (Test-Path 'dist') { Remove-Item -Recurse -Force 'dist' }; New-Item -ItemType Directory -Name 'dist'"
	powershell -Command "cd lambdas/msai-image-uploader; pip install -r requirements.txt -t dist/ --upgrade --platform linux_x86_64 --only-binary=:all:"
	powershell -Command "cd lambdas/msai-image-uploader; Copy-Item -Path main.py, config.py -Destination dist/"
	powershell -Command "cd lambdas/msai-image-uploader; Copy-Item -Path application -Destination dist/ -Recurse -Force"
	powershell -Command "cd lambdas/msai-image-uploader; Copy-Item -Path domain -Destination dist/ -Recurse -Force"
	powershell -Command "cd lambdas/msai-image-uploader; Copy-Item -Path repository -Destination dist/ -Recurse -Force"
	cd lambdas/msai-image-uploader/dist && zip -r ../../../.cloud/terraform/releases/msai-image-uploader.zip .


# Deploy to dev workspace
deploy-dev: 
	@echo "Deploying to dev workspace..."
	cd .cloud/terraform && terraform apply -var-file="workspaces/dev.tfvars" -auto-approve

# Deploy to prod workspace
deploy-prod: build
	@echo "Deploying to prod workspace..."
	cd .cloud/terraform && terraform apply -var-file="workspaces/prod.tfvars" -auto-approve

# Plan for dev workspace
plan-dev:
	@echo "Planning for dev workspace..."
	cd .cloud/terraform && terraform plan -var-file="workspaces/dev.tfvars"

# Plan for prod workspace
plan-prod:
	@echo "Planning for prod workspace..."
	cd .cloud/terraform && terraform plan -var-file="workspaces/prod.tfvars"

destroy-dev:
	@echo "Destroying dev workspace..."
	cd .cloud/terraform && terraform destroy -var-file="workspaces/dev.tfvars" -auto-approve

destroy-prod:
	@echo "Destroying prod workspace..."
	cd .cloud/terraform && terraform destroy -var-file="workspaces/prod.tfvars" 

# Initialize Terraform
init:
	@echo "Initializing Terraform..."
	cd .cloud/terraform && terraform init

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	powershell -Command "if (Test-Path '.cloud/terraform/release/msai-image-uploader.zip') { Remove-Item '.cloud/terraform/release/msai-image-uploader.zip' }"

# Commit and push with message
push:
	@msg="$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))"; \
	git add .; \
	git commit -m "$$msg"; \
	git push origin main

%:
	@:

.PHONY: build deploy-dev deploy-prod plan-dev plan-prod init clean push