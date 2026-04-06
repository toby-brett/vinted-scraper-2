# vinted-scraper-2

An automated deal-finding bot for [Vinted](https://www.vinted.co.uk). Scrapes listings for specific search queries, evaluates pricing using a trained CNN, and sends phone notifications when underpriced items are found.

## How it works

1. **Scraper** - uses Playwright to browse Vinted and collect new listings matching configured search queries
2. **Vision model** - evaluates each listing's image using a CNN trained on scraped Vinted data, predicting a fair market price for the item
3. **Deal detection** - compares the listing price against the model's prediction. If the item is sufficiently underpriced (e.g. £10+ below predicted value and under a target price), it triggers an alert
4. **Alerts** - sends a notification to your phone so you can decide whether to buy and resell

The pricing model is trained such that overpriced and underpriced outliers cancel out, giving a mean prediction close to true market value.

## Project Structure

```
vinted-scraper-2/
├── app/
│   └── scheduler.py      # Entry point — orchestrates scrape/evaluate/alert loop
├── alerts/               # Notification logic (push alerts)
├── config/               # Search queries, thresholds, environment config
├── domain/               # Core data models
├── fetch_stats/          # Stats tracking and logging
├── scraper/              # Playwright-based Vinted scraper
├── storage/              # Persistence layer (seen listings, history)
├── utils/                # Shared utilities
├── vision/               # CNN model definition, training, inference
├── Dockerfile
└── requirements.txt
```

## Stack

- **Python** - core language
- **Playwright** - headless browser scraping with stealth patches
- **PyTorch** - CNN model training and inference
- **scikit-learn** - supporting ML utilities

## Notes

- The CNN was trained on scraped Vinted data, mapping listing images to prices. It is not a general clothing price model — performance varies by category and how well the training data covers the query.
- This project is for personal/educational use. Scraping Vinted may conflict with their Terms of Service.
