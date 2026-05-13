package news

import (
	"bytes"
	"encoding/json"
	"fmt"
	"herekam/internal/models"
	"net/http"
	"net/url"
	"time"
)

type NewsAPIResponse struct {
	Articles []models.Article `json:"articles"`
}

type GDELTArticle struct {
	Title    string `json:"title"`
	URL      string `json:"url"`
	Domain   string `json:"domain"`
	SeenDate string `json:"seendate"`
}

type GDELTResponse struct {
	Articles []GDELTArticle `json:"articles"`
}

var httpClient = &http.Client{
	Timeout: 30 * time.Second,
}

func FetchFromNewsAPI(topic string, apiKey string) ([]models.Article, error) {
	params := url.Values{}
	params.Set("q", topic)
	params.Set("apiKey", apiKey)
	params.Set("pageSize", "20")
	params.Set("language", "en")

	fullURL := "https://newsapi.org/v2/everything?" + params.Encode()

	resp, err := httpClient.Get(fullURL)
	if err != nil {
		return nil, fmt.Errorf("newsapi error: %w", err)
	}
	defer resp.Body.Close()

	var apiResponse NewsAPIResponse
	err = json.NewDecoder(resp.Body).Decode(&apiResponse)
	if err != nil {
		return nil, fmt.Errorf("newsapi decode error: %w", err)
	}

	return apiResponse.Articles, nil
}

func FetchFromGDELT(topic string) ([]models.Article, error) {
	params := url.Values{}
	params.Set("query", topic+" sourcelang:english")
	params.Set("mode", "artlist")
	params.Set("maxrecords", "20")
	params.Set("sort", "datedesc")
	params.Set("format", "json")

	fullURL := "https://api.gdeltproject.org/api/v2/doc/doc?" + params.Encode()

	resp, err := httpClient.Get(fullURL)
	if err != nil {
		fmt.Println("GDELT error:", err)
		return nil, fmt.Errorf("gdelt error: %w", err)
	}
	defer resp.Body.Close()

	var gdeltResp GDELTResponse
	err = json.NewDecoder(resp.Body).Decode(&gdeltResp)
	if err != nil {
		fmt.Println("GDELT decode error:", err)
		return nil, fmt.Errorf("gdelt decode error: %w", err)
	}

	var articles []models.Article
	for _, a := range gdeltResp.Articles {
		articles = append(articles, models.Article{
			Title:       a.Title,
			Description: "",
			URL:         a.URL,
			Source: models.Source{
				ID:   a.Domain,
				Name: a.Domain,
			},
			PublishedAt: a.SeenDate,
			BiasScore:   0,
		})
	}

	fmt.Printf("GDELT fetched: %d articles\n", len(articles))
	return articles, nil
}

func FetchArticles(topic string, apiKey string) ([]models.Article, error) {
	var allArticles []models.Article

	newsAPIArticles, err := FetchFromNewsAPI(topic, apiKey)
	if err != nil {
		fmt.Println("NewsAPI warning:", err)
	} else {
		fmt.Printf("NewsAPI fetched: %d articles\n", len(newsAPIArticles))
		allArticles = append(allArticles, newsAPIArticles...)
	}

	gdeltArticles, err := FetchFromGDELT(topic)
	if err != nil {
		fmt.Println("GDELT warning:", err)
	} else {
		allArticles = append(allArticles, gdeltArticles...)
	}

	fmt.Printf("Total articles fetched: %d\n", len(allArticles))
	return allArticles, nil
}

func ScoreArticles(articles []models.Article) ([]models.Article, error) {
	body, err := json.Marshal(map[string]interface{}{
		"articles": articles,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to marshal articles: %w", err)
	}

	resp, err := httpClient.Post(
		"https://herekam-python.onrender.com",
		"application/json",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to call scorer: %w", err)
	}
	defer resp.Body.Close()

	var result struct {
		Articles []models.Article `json:"articles"`
	}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		return nil, fmt.Errorf("failed to decode scored articles: %w", err)
	}

	return result.Articles, nil
}
