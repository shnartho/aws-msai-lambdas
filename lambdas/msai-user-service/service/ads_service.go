package service

import (
	"context"
	"msai-user-service/model"
	"msai-user-service/repository"
)

type AdsService struct {
	AdsRepo *repository.AdsRepository
}

func NewAdsService(adsRepo *repository.AdsRepository) *AdsService {
	return &AdsService{AdsRepo: adsRepo}
}

func (s *AdsService) CreateAd(ctx context.Context, ad *model.Ad) (string, error) {
	return s.AdsRepo.CreateAd(ctx, ad)
}
func (s *AdsService) GetAdByID(ctx context.Context, adID string) (*model.Ad, error) {
	return s.AdsRepo.GetAdByID(ctx, adID)
}	

func (s *AdsService) UpdateAd(ctx context.Context, adID string, ad *model.UpdateAd) error {
	return s.AdsRepo.UpdateAd(ctx, adID, ad)
}

func (s *AdsService) DeleteAd(ctx context.Context, adID string) error {
	return s.AdsRepo.DeleteAd(ctx, adID)
}	
