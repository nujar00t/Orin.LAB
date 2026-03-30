// Orin.LAB · Signal CLI
// Lightweight Go CLI for generating trading signals from the command line.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

const (
	jupiterAPI = "https://price.jup.ag/v6/price"
	version    = "1.0.0"
)

var knownTokens = map[string]string{
	"SOL":  "So11111111111111111111111111111111111111112",
	"BTC":  "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
	"ETH":  "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
	"JUP":  "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
	"BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
}

type jupiterResponse struct {
	Data map[string]struct {
		Price float64 `json:"price"`
	} `json:"data"`
}

type SignalResult struct {
	Token      string    `json:"token"`
	Price      float64   `json:"price"`
	Signal     string    `json:"signal"`
	Confidence int       `json:"confidence"`
	Timestamp  time.Time `json:"timestamp"`
}

func fetchPrice(mint string) (float64, error) {
	url := fmt.Sprintf("%s?ids=%s", jupiterAPI, mint)
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return 0, err
	}

	var result jupiterResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return 0, err
	}

	if data, ok := result.Data[mint]; ok {
		return data.Price, nil
	}
	return 0, fmt.Errorf("mint %s not found in response", mint)
}

func generateSignal(symbol string, price float64) SignalResult {
	// Simple momentum-based signal
	signal := "HOLD"
	confidence := 50

	// In production this would use real historical data
	// For now use price range heuristics
	switch {
	case symbol == "SOL" && price > 100:
		signal = "BUY"
		confidence = 72
	case symbol == "BTC" && price > 50000:
		signal = "BUY"
		confidence = 68
	case price == 0:
		signal = "HOLD"
		confidence = 0
	}

	return SignalResult{
		Token:      symbol,
		Price:      price,
		Signal:     signal,
		Confidence: confidence,
		Timestamp:  time.Now(),
	}
}

func formatPrice(price float64) string {
	if price >= 1000 {
		return fmt.Sprintf("$%.2f", price)
	}
	if price >= 1 {
		return fmt.Sprintf("$%.4f", price)
	}
	return fmt.Sprintf("$%.8f", price)
}

func printBanner() {
	fmt.Println(`
  ___      _         _      _   ___
 / _ \ _ _(_)_ _   | |    /_\ | _ )
| (_) | '_| | ' \  | |__ / _ \| _ \
 \___/|_| |_|_||_| |____/_/ \_\___/
`)
	fmt.Printf("  Orin.LAB Signal CLI v%s\n\n", version)
}

func main() {
	tokenFlag  := flag.String("token", "SOL", "Token symbol (SOL, BTC, ETH, JUP, BONK)")
	jsonFlag   := flag.Bool("json", false, "Output as JSON")
	allFlag    := flag.Bool("all", false, "Scan all known tokens")
	versionFlag := flag.Bool("version", false, "Show version")
	flag.Parse()

	if *versionFlag {
		fmt.Printf("orin-cli v%s\n", version)
		os.Exit(0)
	}

	if !*jsonFlag {
		printBanner()
	}

	if *allFlag {
		results := []SignalResult{}
		for symbol, mint := range knownTokens {
			price, err := fetchPrice(mint)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error fetching %s: %v\n", symbol, err)
				continue
			}
			result := generateSignal(symbol, price)
			results = append(results, result)

			if !*jsonFlag {
				fmt.Printf("%-6s %12s  %s (%d/100)\n",
					symbol, formatPrice(price), result.Signal, result.Confidence)
			}
		}
		if *jsonFlag {
			enc := json.NewEncoder(os.Stdout)
			enc.SetIndent("", "  ")
			enc.Encode(results)
		}
		return
	}

	symbol := strings.ToUpper(*tokenFlag)
	mint, ok := knownTokens[symbol]
	if !ok {
		fmt.Fprintf(os.Stderr, "Unknown token: %s\nKnown: SOL, BTC, ETH, JUP, BONK\n", symbol)
		os.Exit(1)
	}

	price, err := fetchPrice(mint)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error fetching price: %v\n", err)
		os.Exit(1)
	}

	result := generateSignal(symbol, price)

	if *jsonFlag {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		enc.Encode(result)
		return
	}

	fmt.Printf("Token:      $%s\n", result.Token)
	fmt.Printf("Price:      %s\n", formatPrice(result.Price))
	fmt.Printf("Signal:     %s\n", result.Signal)
	fmt.Printf("Confidence: %d/100\n", result.Confidence)
	fmt.Printf("Time:       %s\n", result.Timestamp.Format(time.RFC3339))
}
