package handler

import (
	"context"
	"encoding/json"
	"msai-auth-service/service"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

// HandleLambda handles AWS Lambda API Gateway proxy requests
func (h *AuthHandler) HandleLambda(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	var resp events.APIGatewayProxyResponse
	resp.Headers = map[string]string{"Content-Type": "application/json"}

	switch event.Path {
	case "/auth/login":
		if event.HTTPMethod != http.MethodPost {
			resp.StatusCode = http.StatusMethodNotAllowed
			return resp, nil
		}
		var req loginRequest
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		token, err := h.AuthService.Login(req.Email, req.Password)
		if err != nil {
			resp.StatusCode = http.StatusUnauthorized
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusOK
		resp.Body = `{"token":"` + token + `"}`
		return resp, nil

	case "/auth/signup":
		if event.HTTPMethod != http.MethodPost {
			resp.StatusCode = http.StatusMethodNotAllowed
			return resp, nil
		}
		var req signupRequest
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		err := h.AuthService.Signup(req.Email, req.Password, req.Region, req.Balance)
		if err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusCreated
		resp.Body = `{"message":"user created"}`
		return resp, nil

	default:
		resp.StatusCode = http.StatusNotFound
		resp.Body = `{"error":"not found"}`
		return resp, nil
	}
}

type AuthHandler struct {
	AuthService *service.AuthService
}

type loginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type signupRequest struct {
	Email    string  `json:"email"`
	Password string  `json:"password"`
	Region   string  `json:"region"`
	Balance  float64 `json:"balance"`
}
