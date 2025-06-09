# Build the Lambda function package
build:
	@echo "Building Lambda function package..."
	powershell -Command "cd lambdas/hello_world; Compress-Archive -Path * -DestinationPath '../../.cloud/terraform/releases/hello_world.zip' -Force"

# Deploy to dev workspace
deploy-dev: build
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
	powershell -Command "if (Test-Path '.cloud/terraform/hello_world.zip') { Remove-Item '.cloud/terraform/hello_world.zip' }"

# Commit and push with message
push:
	@msg="$(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))"; \
	git add .; \
	git commit -m "$$msg"; \
	git push origin main

%:
	@:

.PHONY: build deploy-dev deploy-prod plan-dev plan-prod init clean push