package main

import (
	"fmt"
	"net/http"
	"os"

	"herekam/config"
	"herekam/internal/news"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	sendgrid "github.com/sendgrid/sendgrid-go"
	"github.com/sendgrid/sendgrid-go/helpers/mail"
)

func sendVisitorEmail(topic string, ip string, userAgent string) {
	from := mail.NewEmail("Herekam", "gleorush24@gmail.com")
	to := mail.NewEmail("Gordon", "aebusulinagekalu@gmail.com")
	subject := "🌏 New Herekam Search!"
	body := fmt.Sprintf(`
New search on Herekam!

Topic searched: %s
IP Address: %s
Device/Browser: %s
Time: now

Harim nao! 🎙️
	`, topic, ip, userAgent)

	message := mail.NewSingleEmail(from, subject, to, body, "")
	apiKey := os.Getenv("SENDGRID_API_KEY")
	if apiKey == "" {
    fmt.Println("Warning: SENDGRID_API_KEY not set")
    return
}
	client := sendgrid.NewSendClient(apiKey)
	_, err := client.Send(message)
	if err != nil {
		fmt.Println("Email error:", err)
	} else {
		fmt.Println("Email sent!")
	}
}

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
		userAgent := c.Request.UserAgent()

		if topic == "" {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "topic is required",
			})
			return
		}

		// Send email notification
		go sendVisitorEmail(topic, ip, userAgent)

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
