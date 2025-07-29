package service

import (
	"errors"
	"msai-user-service/model"
	"msai-user-service/repository"
	"msai-user-service/util"
)

type AuthService struct {
	userRepo *repository.UserRepository
}

func NewAuthService(userRepo *repository.UserRepository) *AuthService {
	return &AuthService{userRepo: userRepo}
}

func (s *AuthService) Login(email, password string) (string, error) {
	loginUser, err := s.userRepo.GetLoginUserByEmail(email)
	if err != nil {
		return "", errors.New("invalid credentials")
	}
	if !util.CheckPasswordHash(password, loginUser.Password) {
		return "", errors.New("invalid credentials")
	}
	token, err := util.GenerateJWT(loginUser.Email, loginUser.ID)
	if err != nil {
		return "", err
	}
	return token, nil
}

func (s *AuthService) Signup(email, password, region string, balance float64) error {
	hash, err := util.HashPassword(password)
	if err != nil {
		return err
	}
	user := model.NewSignupUser(email, hash, region, balance)
	return s.userRepo.CreateSignupUser(user)
}
