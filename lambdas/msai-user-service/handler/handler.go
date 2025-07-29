package handler

import (
	"context"
	"encoding/json"
	"msai-user-service/service"
	"msai-user-service/util"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

type Handler struct {
	AuthService *service.AuthService
	UserService *service.UserService
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

var (
	msgUserCreated = `{"message":"user created"}`
)
var (
	errInvalidRequestBody = `{"error":"invalid request body"}`
	errUnauthorized       = `{"error":"unauthorized"}`
	errUserExists         = `{"error":"user already exists"}`
	errSignup             = `{"error":"signup failed"}`
	errNotFound           = `{"error":"path not found"}`
)

func (h *Handler) HandleLambda(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	switch event.Path {
	case "/user/status":
		return h.handleUserStatusRequest(event)
	case "/user/balance":
		return h.handleUserBalanceRequest(ctx, event)
	case "/user/profile":
		return h.handleUserProfileRequest(event)
	case "/auth/login":
		return h.handleLoginRequest(event)
	case "/auth/signup":
		return h.handleSignupRequest(event)
	default:
		return events.APIGatewayProxyResponse{
			StatusCode: http.StatusNotFound,
			Headers:    map[string]string{"Content-Type": "application/json"},
			Body:       errNotFound,
		}, nil
	}
}

func (h *Handler) handleUserStatusRequest(event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}
	if event.HTTPMethod != http.MethodGet {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}
	resp.StatusCode = http.StatusOK
	resp.Body = `{"status":"OK"}`
	return resp, nil
}

func (h *Handler) handleUserBalanceRequest(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}
	if event.HTTPMethod != http.MethodPatch {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}

	tokenClaims, err := util.ExtractAndValidateJWT(event.Headers)
	if err != nil {
		resp.StatusCode = http.StatusUnauthorized
		resp.Body = errUnauthorized
		return resp, nil
	}

	var body struct {
		Balance float64 `json:"balance"`
	}
	if err := json.Unmarshal([]byte(event.Body), &body); err != nil {
		resp.StatusCode = http.StatusBadRequest
		resp.Body = errInvalidRequestBody
		return resp, nil
	}

	err = h.UserService.UpdateBalance(ctx, tokenClaims.Subject, body.Balance)
	if err != nil {
		resp.StatusCode = http.StatusBadRequest
		resp.Body = `{"error":"` + err.Error() + `"}`
		return resp, nil
	}

	resp.StatusCode = http.StatusOK
	resp.Body = `{"message":"balance updated"}`
	return resp, nil
}

func (h *Handler) handleLoginRequest(event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}
	if event.HTTPMethod != http.MethodPost {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}
	var req loginRequest
	if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
		resp.StatusCode = http.StatusBadRequest
		resp.Body = errInvalidRequestBody
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
}

func (h *Handler) handleSignupRequest(event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}
	if event.HTTPMethod != http.MethodPost {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}
	var req signupRequest
	if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
		resp.StatusCode = http.StatusBadRequest
		resp.Body = errInvalidRequestBody
		return resp, nil
	}
	err := h.AuthService.Signup(req.Email, req.Password, req.Region, req.Balance)
	if err != nil {
		resp.StatusCode = http.StatusBadRequest
		resp.Body = `{"error":"` + err.Error() + `"}`
		return resp, nil
	}
	resp.StatusCode = http.StatusCreated
	resp.Body = msgUserCreated
	return resp, nil
}

func (h *Handler) handleUserProfileRequest(event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}
	if event.HTTPMethod != http.MethodGet {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}

	tokenClaims, err := util.ExtractAndValidateJWT(event.Headers)
	if err != nil {
		resp.StatusCode = http.StatusUnauthorized
		resp.Body = errUnauthorized
		return resp, nil
	}

	user, err := h.UserService.GetUserProfile(context.Background(), tokenClaims.Subject)
	if err != nil {
		resp.StatusCode = http.StatusNotFound
		resp.Body = `{"error":"user not found"}`
		return resp, nil
	}
	body, err := json.Marshal(user)
	if err != nil {
		resp.StatusCode = http.StatusInternalServerError
		resp.Body = `{"error":"` + err.Error() + `"}`
		return resp, nil
	}

	resp.StatusCode = http.StatusOK
	resp.Body = string(body)
	return resp, nil
}