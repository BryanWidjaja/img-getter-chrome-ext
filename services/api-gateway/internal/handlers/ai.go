package handlers

import (
	"bytes"
	"io"
	"log"
	"net/http"

	pbAI "github.com/RarityValue/img-getter-chrome-ext/protos/ai"
	"github.com/gin-gonic/gin"
)

func (h *Gateway) PredictHashtags(c *gin.Context) {
	file, _, err := c.Request.FormFile("image")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Image file is required"})
		return
	}
	defer file.Close()

	buf := bytes.NewBuffer(nil)
	if _, err := io.Copy(buf, file); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read image file"})
		return
	}

	resp, err := h.AIClient.PredictHashtags(c.Request.Context(), &pbAI.PredictRequest{
		ImageData: buf.Bytes(),
	})

	if err != nil {
		log.Printf("AI Service Error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate hashtags"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"hashtags": resp.Hashtags,
	})

}
