package main

import (
	"context"
	"log"
	"msai-auth-service/handler"
	"msai-auth-service/repository"
	"msai-auth-service/service"

	"github.com/aws/aws-lambda-go/lambda"
	"go.uber.org/fx"
)

func main() {
	var authHandler *handler.AuthHandler
	app := fx.New(
		fx.Provide(
			repository.NewUserRepository,
			service.NewAuthService,
			func(authService *service.AuthService) *handler.AuthHandler {
				return &handler.AuthHandler{AuthService: authService}
			},
		),
		fx.Populate(&authHandler),
	)
	startCtx, cancel := context.WithTimeout(context.Background(), fx.DefaultTimeout)
	defer cancel()
	if err := app.Start(startCtx); err != nil {
		log.Fatalf("failed to start fx app: %v", err)
	}
	defer app.Stop(context.Background())

	// Use the handler's HandleLambda method as the Lambda entrypoint
	lambda.Start(authHandler.HandleLambda)
}
