package repository

import (
	"context"
	"errors"
	"fmt"
	"msai-user-service/model"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

const (
	adsTable = "msai.ads"
)

type AdsRepository struct {
	db    *dynamodb.Client
	table string
}

func NewAdsRepository() (*AdsRepository, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		return nil, err
	}
	db := dynamodb.NewFromConfig(cfg)
	return &AdsRepository{db: db, table: adsTable}, nil
}

func (r *AdsRepository) GetAdByID(ctx context.Context, adID string) (*model.Ad, error) {
	input := &dynamodb.GetItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: adID},
		},
	}
	result, err := r.db.GetItem(ctx, input)
	if err != nil || result.Item == nil {
		return nil, errors.New("ad not found")
	}
	var ad model.Ad
	err = attributevalue.UnmarshalMap(result.Item, &ad)
	if err != nil {
		return nil, err
	}
	return &ad, nil
}

func (r *AdsRepository) UpdateAd(ctx context.Context, adID string, ad *model.UpdateAd) error {
	updateExpr := "SET "
	exprAttrValues := make(map[string]types.AttributeValue)
	exprAttrNames := make(map[string]string)
	first := true

	if ad.Title != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#T = :title"
		exprAttrNames["#T"] = "title"
		exprAttrValues[":title"] = &types.AttributeValueMemberS{Value: *ad.Title}
	}
	if ad.Description != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#D = :desc"
		exprAttrNames["#D"] = "description"
		exprAttrValues[":desc"] = &types.AttributeValueMemberS{Value: *ad.Description}
	}
	if ad.ImageURL != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#I = :img"
		exprAttrNames["#I"] = "image_url"
		exprAttrValues[":img"] = &types.AttributeValueMemberS{Value: *ad.ImageURL}
	}
	if ad.Active != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#A = :active"
		exprAttrNames["#A"] = "active"
		exprAttrValues[":active"] = &types.AttributeValueMemberBOOL{Value: *ad.Active}
	}
	if ad.Region != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#R = :region"
		exprAttrNames["#R"] = "region"
		exprAttrValues[":region"] = &types.AttributeValueMemberS{Value: *ad.Region}
	}
	if ad.Budget != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#B = :budget"
		exprAttrNames["#B"] = "budget"
		exprAttrValues[":budget"] = &types.AttributeValueMemberN{Value: fmt.Sprintf("%f", *ad.Budget)}
	}
	if ad.ViewCount != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#VC = :vc"
		exprAttrNames["#VC"] = "view_count"
		exprAttrValues[":vc"] = &types.AttributeValueMemberN{Value: fmt.Sprintf("%d", *ad.ViewCount)}
	}
	if ad.RewardPerView != nil {
		if !first {
			updateExpr += ", "
		} else {
			first = false
		}
		updateExpr += "#RPV = :rpv"
		exprAttrNames["#RPV"] = "reward_per_view"
		exprAttrValues[":rpv"] = &types.AttributeValueMemberN{Value: fmt.Sprintf("%f", *ad.RewardPerView)}
	}

	if first {
		// No fields to update
		return nil
	}

	input := &dynamodb.UpdateItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: adID},
		},
		UpdateExpression:          aws.String(updateExpr),
		ExpressionAttributeValues: exprAttrValues,
		ExpressionAttributeNames:  exprAttrNames,
	}
	_, err := r.db.UpdateItem(ctx, input)
	return err
}

func (r *AdsRepository) CreateAd(ctx context.Context, ad *model.Ad) (string, error) {
	item, err := attributevalue.MarshalMap(ad)
	if err != nil {
		return "", err
	}
	input := &dynamodb.PutItemInput{
		TableName:           &r.table,
		Item:                item,
		ConditionExpression: aws.String("attribute_not_exists(id)"),
	}
	_, err = r.db.PutItem(ctx, input)
	if err != nil {
		return "", err
	}
	return ad.ID, nil
}

func (r *AdsRepository) DeleteAd(ctx context.Context, adID string) error {
	input := &dynamodb.DeleteItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: adID},
		},
	}
	_, err := r.db.DeleteItem(ctx, input)
	return err
}
