package service

import (
	"context"
	"msai-user-service/model"
	"msai-user-service/repository"
)

type UserService struct {
	UserRepo *repository.UserRepository
}

func NewUserService(userRepo *repository.UserRepository) *UserService {
	return &UserService{UserRepo: userRepo}
}

func (s *UserService) UpdateBalance(ctx context.Context, userID string, balance float64) error {
	return s.UserRepo.UpdateUserBalance(ctx, userID, balance)
}

func (s *UserService) GetUserProfile(ctx context.Context, userID string) (*model.User, error) {
	return s.UserRepo.GetUserByID(ctx, userID)
}

func (s *UserService) DeleteUserProfile(ctx context.Context, userID string) error {
	return s.UserRepo.DeleteUserByID(ctx, userID)
}
