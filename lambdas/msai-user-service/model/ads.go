package model

import (
	"time"

	"github.com/google/uuid"
)

type Ad struct {
	ID              string  `json:"id" dynamodbav:"id"`
	Title           string  `json:"title" dynamodbav:"title"`
	ImageURL        string  `json:"image_url" dynamodbav:"image_url"`
	Description     string  `json:"description" dynamodbav:"description"`
	PostedBy        string  `json:"posted_by" dynamodbav:"posted_by"`
	Active          bool    `json:"active" dynamodbav:"active"`
	Region          string  `json:"region" dynamodbav:"region"`
	Budget          float64 `json:"budget" dynamodbav:"budget"`
	CreatedAt       int64   `json:"created_at" dynamodbav:"created_at"`
	ExpiresAt       *int64  `json:"expires_at" dynamodbav:"expires_at"`
	ViewCount       int64   `json:"view_count" dynamodbav:"view_count"`
	RewardPerView   float64 `json:"reward_per_view" dynamodbav:"reward_per_view"`
	RemainingBudget float64 `json:"remaining_budget" dynamodbav:"remaining_budget"`
}

func NewAd(title, imageURL, description, postedBy, region string, budget, rewardPerView float64) *Ad {
	now := time.Now()
	expiresAt := now.Add(7 * 24 * time.Hour).Unix()
	return &Ad{
		ID:              uuid.New().String(),
		Title:           title,
		ImageURL:        imageURL,
		Description:     description,
		PostedBy:        postedBy,
		Active:          true,
		Region:          region,
		Budget:          budget,
		CreatedAt:       now.Unix(),
		ExpiresAt:       &expiresAt,
		ViewCount:       0,
		RewardPerView:   rewardPerView,
		RemainingBudget: budget, // Initial RemainingBudget = budget
	}
}

type UpdateAd struct {
	Title         *string  `json:"title" dynamodbav:"title"`
	ImageURL      *string  `json:"image_url" dynamodbav:"image_url"`
	Description   *string  `json:"description" dynamodbav:"description"`
	Active        *bool    `json:"active" dynamodbav:"active"`
	Region        *string  `json:"region" dynamodbav:"region"`
	Budget        *float64 `json:"budget" dynamodbav:"budget"`
	ViewCount     *int64   `json:"view_count" dynamodbav:"view_count"`
	RewardPerView *float64 `json:"reward_per_view" dynamodbav:"reward_per_view"`
}

func (a *Ad) ToUpdateAd() *UpdateAd {
	return &UpdateAd{
		Title:         &a.Title,
		ImageURL:      &a.ImageURL,
		Description:   &a.Description,
		Active:        &a.Active,
		Region:        &a.Region,
		Budget:        &a.Budget,
		ViewCount:     &a.ViewCount,
		RewardPerView: &a.RewardPerView,
	}
}
