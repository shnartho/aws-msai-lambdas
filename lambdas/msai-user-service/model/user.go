package model

import "github.com/google/uuid"

type User struct {
	ID       string  `json:"id" dynamodbav:"id"`
	Email    string  `json:"email" dynamodbav:"email"`
	Region   string  `json:"region" dynamodbav:"region"`
	Balance  float64 `json:"balance" dynamodbav:"balance"`
}

func NewUser(email, password, region string, balance float64) *User {
	return &User{
		ID:       uuid.New().String(),
		Email:    email,
		Region:   region,
		Balance:  balance,
	}
}

type LoginUser struct {
	ID       string  `json:"id" dynamodbav:"id"`
	Email    string  `json:"email" dynamodbav:"email"`
	Password string  `json:"password" dynamodbav:"password"`
}

// Private struct for creating a new user during signup
type SignupUser struct {
	ID       string  `json:"id" dynamodbav:"id"`
	Email    string  `json:"email" dynamodbav:"email"`
	Password string  `json:"password" dynamodbav:"password"`
	Region   string  `json:"region" dynamodbav:"region"`
	Balance  float64 `json:"balance" dynamodbav:"balance"`
}
func NewSignupUser(email, password, region string, balance float64) *SignupUser {
	return &SignupUser{
		ID:       uuid.New().String(),
		Email:    email,
		Password: password,
		Region:   region,
		Balance:  balance,
	}
}
