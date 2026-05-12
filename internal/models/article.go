package models

type Source struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type RegionalScores struct {
	USBias      float64 `json:"us_bias"`
	AUSBias     float64 `json:"aus_bias"`
	ChinaBias   float64 `json:"china_bias"`
	PacificBias float64 `json:"pacific_bias"`
}

type Article struct {
	Title          string          `json:"title"`
	Description    string          `json:"description"`
	URL            string          `json:"url"`
	Source         Source          `json:"source"`
	PublishedAt    string          `json:"publishedAt"`
	BiasScore      float64         `json:"bias_score"`
	RegionalScores *RegionalScores `json:"regional_scores"`
}
