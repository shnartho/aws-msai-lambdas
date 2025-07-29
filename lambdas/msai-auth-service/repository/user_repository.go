package repository

import (
	"context"
	"errors"
	"msai-auth-service/model"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
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
	return &UserRepository{db: db, table: "msai.user"}, nil
}

func (r *UserRepository) GetUserByEmail(email string) (*model.User, error) {
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
	}
	result, err := r.db.Query(context.TODO(), input)
	if err != nil || len(result.Items) == 0 {
		return nil, errors.New("user not found")
	}
	var user model.User
	err = attributevalue.UnmarshalMap(result.Items[0], &user)
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) CreateUser(user *model.User) error {
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
