# MetaSurfAI Lambda Functions

AWS Lambda functions for the MetaSurfAI platform, deployed with Terraform.

## Quick Start

```bash
# Initialize
make init

# Deploy to dev
make deploy-dev

# Deploy to prod
make deploy-prod
```

## Structure

```
lambdas/           # Lambda function code
.cloud/terraform/  # Infrastructure as code
Makefile          # Build & deploy commands
```

## Commands

| Command | Description |
|---------|-------------|
| `make build` | Package Lambda functions |
| `make init` | Initialize Terraform |
| `make plan-dev` | Plan dev deployment |
| `make deploy-dev` | Deploy to dev |
| `make plan-prod` | Plan prod deployment |
| `make deploy-prod` | Deploy to prod |

## Adding Functions

1. Create folder in `lambdas/`
2. Add Python code
3. Update Terraform config
4. Deploy with `make deploy-dev`



