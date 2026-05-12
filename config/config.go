package config

import "os"

type Config struct {
	NewsAPIKey string
	Port       string
}

func Load() Config {
	newsAPIKey := os.Getenv("NEWS_API_KEY")
	if newsAPIKey == "" {
		newsAPIKey: "ada9eb876f384277acf4445bfafc4c66"
	}
	return Config{
		NewsAPIKey: newsAPIKey,
		Port:       ":8080",
	}
}
