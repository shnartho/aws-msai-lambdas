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
	userTable = "msai.user"
)

type UserRepository struct {
	db    *dynamodb.Client
	table string
}

func NewUserRepository() (*UserRepository, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		return nil, err
	}
	db := dynamodb.NewFromConfig(cfg)
	return &UserRepository{db: db, table: userTable}, nil
}

func (r *UserRepository) GetLoginUserByEmail(email string) (model.LoginUser, error) {
	input := &dynamodb.QueryInput{
		TableName: &r.table,
		IndexName: aws.String("email-index"),
		KeyConditions: map[string]types.Condition{
			"email": {
				ComparisonOperator: types.ComparisonOperatorEq,
				AttributeValueList: []types.AttributeValue{
					&types.AttributeValueMemberS{Value: email},
				},
			},
		},
		ProjectionExpression: aws.String("id,email,password"),
		Limit:                aws.Int32(1),
	}
	result, err := r.db.Query(context.TODO(), input)
	if err != nil || len(result.Items) == 0 {
		return model.LoginUser{}, errors.New("user not found")
	}
	var loginUser model.LoginUser
	err = attributevalue.UnmarshalMap(result.Items[0], &loginUser)
	if err != nil {
		return model.LoginUser{}, err
	}
	return loginUser, nil
}

func (r *UserRepository) UpdateUserBalance(ctx context.Context, userID string, balance float64) error {
	input := &dynamodb.UpdateItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: userID},
		},
		UpdateExpression:          aws.String("SET balance = :balance"),
		ExpressionAttributeValues: map[string]types.AttributeValue{":balance": &types.AttributeValueMemberN{Value: fmt.Sprintf("%f", balance)}},
	}
	_, err := r.db.UpdateItem(ctx, input)
	return err
}

func (r *UserRepository) CreateSignupUser(user *model.SignupUser) error {
	item, err := attributevalue.MarshalMap(user)
	if err != nil {
		return err
	}
	_, err = r.db.PutItem(context.TODO(), &dynamodb.PutItemInput{
		TableName: &r.table,
		Item:      item,
	})
	return err
}

func (r *UserRepository) GetUserByID(ctx context.Context, userID string) (*model.User, error) {
	input := &dynamodb.GetItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: userID},
		},
	}
	result, err := r.db.GetItem(ctx, input)
	if err != nil || result.Item == nil {
		return nil, errors.New("user not found")
	}
	var user model.User
	err = attributevalue.UnmarshalMap(result.Item, &user)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) DeleteUserByID(ctx context.Context, userID string) error {
	input := &dynamodb.DeleteItemInput{
		TableName: &r.table,
		Key: map[string]types.AttributeValue{
			"id": &types.AttributeValueMemberS{Value: userID},
		},
	}
	_, err := r.db.DeleteItem(ctx, input)
	return err
}
