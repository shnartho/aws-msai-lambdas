package util

import (
	"time"

	"github.com/golang-jwt/jwt/v4"
)

var jwtKey = []byte("secret")

func GenerateJWT(email string) (string, error) {
	claims := &jwt.RegisteredClaims{
		Subject:   email,
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtKey)
}
