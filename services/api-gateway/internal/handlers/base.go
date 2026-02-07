package handlers

import (
	pbAI "github.com/RarityValue/img-getter-chrome-ext/protos/ai"
)

type Gateway struct {
	AIClient pbAI.AIServiceClient
}

func GatewayHandler(aiClient pbAI.AIServiceClient) *Gateway {
	return &Gateway{
		AIClient: aiClient,
	}
}
