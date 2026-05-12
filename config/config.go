package config

type Config struct {
	NewsAPIKey string
	Port       string
}

func Load() Config {
	return Config{
		NewsAPIKey: "ada9eb876f384277acf4445bfafc4c66",
		Port:       ":8080",
	}
}
