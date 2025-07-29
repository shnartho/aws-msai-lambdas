package model

import "github.com/google/uuid"

type User struct {
	ID       string  `json:"id" dynamodbav:"id"`
	Email    string  `json:"email" dynamodbav:"email"`
	Password string  `json:"password" dynamodbav:"password"`
	Region   string  `json:"region" dynamodbav:"region"`
	Balance  float64 `json:"balance" dynamodbav:"balance"`
}

func NewUser(email, password, region string, balance float64) *User {
	return &User{
		ID:       uuid.New().String(),
		Email:    email,
		Password: password,
		Region:   region,
		Balance:  balance,
	}
}
