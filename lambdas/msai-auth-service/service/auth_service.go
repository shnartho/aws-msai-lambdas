package service

import (
	"errors"
	"msai-auth-service/model"
	"msai-auth-service/repository"
	"msai-auth-service/util"
)

type AuthService struct {
	userRepo *repository.UserRepository
}

func NewAuthService(userRepo *repository.UserRepository) *AuthService {
	return &AuthService{userRepo: userRepo}
}

func (s *AuthService) Login(email, password string) (string, error) {
	user, err := s.userRepo.GetUserByEmail(email)
	if err != nil {
		return "", errors.New("invalid credentials")
	}
	if !util.CheckPasswordHash(password, user.Password) {
		return "", errors.New("invalid credentials")
	}
	token, err := util.GenerateJWT(user.Email)
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
	user := model.NewUser(email, hash, region, balance)
	return s.userRepo.CreateUser(user)
}
