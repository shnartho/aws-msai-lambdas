package handler

import (
	"context"
	"encoding/json"
	"msai-user-service/model"
	"msai-user-service/service"
	"msai-user-service/util"
	"net/http"

	"github.com/aws/aws-lambda-go/events"
)

type Handler struct {
	AuthService *service.AuthService
	UserService *service.UserService
	AdsService  *service.AdsService
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
	msgUserCreated = `{"message":"user created successfully"}`
	msgUserDeleted = `{"message":"user deleted successfully"}`
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
	case "/status":
		return h.handleUserStatusRequest(event)
	case "/user/balance":
		return h.handleUserBalanceRequest(ctx, event)
	case "/user/profile":
		return h.handleUserProfileRequest(event)
	case "/ads":
		return h.handleAdsRequest(ctx, event)
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

	if event.HTTPMethod != http.MethodGet && event.HTTPMethod != http.MethodDelete {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}

	tokenClaims, err := util.ExtractAndValidateJWT(event.Headers)
	if err != nil {
		resp.StatusCode = http.StatusUnauthorized
		resp.Body = errUnauthorized
		return resp, nil
	}

	switch event.HTTPMethod {
	case http.MethodGet:
		user, err := h.UserService.GetUserProfile(context.Background(), tokenClaims.Subject)
		if err != nil || user == nil {
			resp.StatusCode = http.StatusNotFound
			resp.Body = `{"error":"user not found"}`
			return resp, nil
		}
		body, _ := json.Marshal(user)
		resp.StatusCode = http.StatusOK
		resp.Body = string(body)
	case http.MethodDelete:
		err := h.UserService.DeleteUserProfile(context.Background(), tokenClaims.Subject)
		if err != nil {
			resp.StatusCode = http.StatusInternalServerError
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusOK
		resp.Body = msgUserDeleted
	}

	return resp, nil
}

func (h *Handler) handleAdsRequest(ctx context.Context, event events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	resp := events.APIGatewayProxyResponse{Headers: map[string]string{"Content-Type": "application/json"}}

	if event.HTTPMethod != http.MethodGet && event.HTTPMethod != http.MethodPost && event.HTTPMethod != http.MethodPatch && event.HTTPMethod != http.MethodDelete {
		resp.StatusCode = http.StatusMethodNotAllowed
		return resp, nil
	}

	tokenClaims, err := util.ExtractAndValidateJWT(event.Headers)
	if err != nil {
		resp.StatusCode = http.StatusUnauthorized
		resp.Body = errUnauthorized
		return resp, nil
	}

	switch event.HTTPMethod {
	case http.MethodGet:
		var req struct {
			ID string `json:"id"`
		}
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		ads, err := h.AdsService.GetAdByID(ctx, req.ID)
		if err != nil {
			resp.StatusCode = http.StatusInternalServerError
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		body, _ := json.Marshal(ads)
		resp.StatusCode = http.StatusOK
		resp.Body = string(body)
	case http.MethodPost:
		var req struct {
			Title         string  `json:"title"`
			ImageURL      string  `json:"image_url"`
			Description   string  `json:"description"`
			Region        string  `json:"region"`
			Budget        float64 `json:"budget"`
			RewardPerView float64 `json:"reward_per_view"`
		}
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		ad := model.NewAd(
			req.Title,
			req.ImageURL,
			req.Description,
			tokenClaims.Subject,
			req.Region,
			req.Budget,
			req.RewardPerView,
		)
		id, err := h.AdsService.CreateAd(ctx, ad)
		if err != nil {
			resp.StatusCode = http.StatusInternalServerError
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusCreated
		resp.Body = `{"message":"ad created successfully", "id":"` + id + `"}`

	case http.MethodPatch:
		var req struct {
			ID            string   `json:"id"`
			Title         *string  `json:"title"`
			ImageURL      *string  `json:"image_url"`
			Description   *string  `json:"description"`
			Region        *string  `json:"region"`
			Active        *bool    `json:"active"`
			ViewCount     *int64   `json:"view_count"`
			Budget        *float64 `json:"budget"`
			RewardPerView *float64 `json:"reward_per_view"`
		}
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		updateAd := &model.UpdateAd{
			Title:         req.Title,
			ImageURL:      req.ImageURL,
			Description:   req.Description,
			Region:        req.Region,
			Active:        req.Active,
			Budget:        req.Budget,
			RewardPerView: req.RewardPerView,
			ViewCount:     req.ViewCount,
		}
		err := h.AdsService.UpdateAd(ctx, req.ID, updateAd)
		if err != nil {
			resp.StatusCode = http.StatusInternalServerError
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusOK
		resp.Body = `{"message":"ad updated successfully", "id":"` + req.ID + `"}`
	case http.MethodDelete:
		var req struct {
			ID string `json:"id"`
		}
		if err := json.Unmarshal([]byte(event.Body), &req); err != nil {
			resp.StatusCode = http.StatusBadRequest
			resp.Body = `{"error":"invalid request body"}`
			return resp, nil
		}
		err := h.AdsService.DeleteAd(ctx, req.ID)
		if err != nil {
			resp.StatusCode = http.StatusInternalServerError
			resp.Body = `{"error":"` + err.Error() + `"}`
			return resp, nil
		}
		resp.StatusCode = http.StatusOK
		resp.Body = `{"message":"ad deleted successfully", "id":"` + req.ID + `"}`
	}

	return resp, nil
}
