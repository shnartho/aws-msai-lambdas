package main

import (
	"context"
	"log"
	"msai-user-service/handler"
	"msai-user-service/repository"
	"msai-user-service/service"

	"github.com/aws/aws-lambda-go/lambda"
	"go.uber.org/fx"
)

func main() {
	var Handler *handler.Handler
	app := fx.New(
		fx.Provide(
			repository.NewUserRepository,
			repository.NewAdsRepository,
			service.NewAuthService,
			service.NewUserService,
			service.NewAdsService,
			func(authService *service.AuthService, userService *service.UserService, adsService *service.AdsService) *handler.Handler {
				return &handler.Handler{
					AuthService: authService,
					UserService: userService,
					AdsService:  adsService,
				}
			},
		),
		fx.Populate(&Handler),
	)
	startCtx, cancel := context.WithTimeout(context.Background(), fx.DefaultTimeout)
	defer cancel()
	if err := app.Start(startCtx); err != nil {
		log.Fatalf("failed to start fx app: %v", err)
	}
	defer app.Stop(context.Background())

	// Use the handler's HandleLambda method as the Lambda entrypoint
	lambda.Start(Handler.HandleLambda)
}
