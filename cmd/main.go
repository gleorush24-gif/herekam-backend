package main

import (
	"fmt"
	"net/http"

	"herekam/config"
	"herekam/internal/news"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	fmt.Println("Herekam is starting...")

	cfg := config.Load()
	router := gin.Default()
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"*"},
		AllowCredentials: false,
	}))

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Herekam!",
			"status":  "running",
		})
	})

	router.GET("/news", func(c *gin.Context) {
		topic := c.Query("topic")
		ip := c.ClientIP()
		fmt.Printf("Search: topic=%s ip=%s\n", topic, ip)

		if topic == "" {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "topic is required",
			})
			return
		}

		articles, err := news.FetchArticles(topic, cfg.NewsAPIKey)
		if err != nil {
			fmt.Println("Fetch error:", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": err.Error(),
			})
			return
		}

		scoredArticles, err := news.ScoreArticles(articles)
		if err != nil {
			fmt.Println("Scoring error:", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"topic":    topic,
			"count":    len(scoredArticles),
			"articles": scoredArticles,
		})
	})

	if err := router.Run(cfg.Port); err != nil {
		fmt.Println("Error starting server:", err)
	}
}
