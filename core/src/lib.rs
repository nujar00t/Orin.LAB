/// Orin.LAB · Core SDK
/// High-performance data processing core in Rust.

/// Represents a price data point.
#[derive(Debug, Clone, PartialEq)]
pub struct PricePoint {
    pub price: f64,
    pub timestamp: u64,
}

/// Signal direction.
#[derive(Debug, Clone, PartialEq)]
pub enum Signal {
    Buy,
    Sell,
    Hold,
}

impl std::fmt::Display for Signal {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Signal::Buy  => write!(f, "BUY"),
            Signal::Sell => write!(f, "SELL"),
            Signal::Hold => write!(f, "HOLD"),
        }
    }
}

/// Result of a signal computation.
#[derive(Debug, Clone)]
pub struct SignalResult {
    pub signal: Signal,
    pub confidence: u8,
    pub reason: String,
}

/// Compute a momentum-based signal from a price series.
///
/// Returns `None` if the series has fewer than 3 data points.
pub fn compute_signal(prices: &[f64]) -> Option<SignalResult> {
    if prices.len() < 3 {
        return None;
    }

    let latest  = prices[prices.len() - 1];
    let prev    = prices[prices.len() - 2];
    let oldest  = prices[0];

    if prev == 0.0 || oldest == 0.0 {
        return None;
    }

    let recent_change  = (latest - prev) / prev;
    let overall_change = (latest - oldest) / oldest;

    let (signal, confidence, reason) = if recent_change > 0.02 && overall_change > 0.05 {
        let conf = ((overall_change.abs() * 100.0 + 50.0).min(95.0)) as u8;
        (
            Signal::Buy,
            conf,
            format!(
                "Upward momentum: {:.2}% recent, {:.2}% overall",
                recent_change * 100.0,
                overall_change * 100.0
            ),
        )
    } else if recent_change < -0.02 && overall_change < -0.05 {
        let conf = ((overall_change.abs() * 100.0 + 50.0).min(95.0)) as u8;
        (
            Signal::Sell,
            conf,
            format!(
                "Downward momentum: {:.2}% recent, {:.2}% overall",
                recent_change * 100.0,
                overall_change * 100.0
            ),
        )
    } else {
        (Signal::Hold, 50, "No clear momentum signal".to_string())
    };

    Some(SignalResult { signal, confidence, reason })
}

/// Calculate simple moving average.
pub fn sma(prices: &[f64], period: usize) -> Option<f64> {
    if prices.len() < period || period == 0 {
        return None;
    }
    let slice = &prices[prices.len() - period..];
    Some(slice.iter().sum::<f64>() / period as f64)
}

/// Calculate price volatility (standard deviation).
pub fn volatility(prices: &[f64]) -> Option<f64> {
    if prices.len() < 2 {
        return None;
    }
    let mean = prices.iter().sum::<f64>() / prices.len() as f64;
    let variance = prices.iter().map(|p| (p - mean).powi(2)).sum::<f64>() / prices.len() as f64;
    Some(variance.sqrt())
}

/// Format a price value for display.
pub fn format_price(price: f64) -> String {
    if price >= 1_000.0 {
        format!("${:.2}", price)
    } else if price >= 1.0 {
        format!("${:.4}", price)
    } else {
        format!("${:.8}", price)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_signal_buy() {
        let prices = vec![100.0, 103.0, 107.0];
        let result = compute_signal(&prices).unwrap();
        assert_eq!(result.signal, Signal::Buy);
        assert!(result.confidence > 50);
    }

    #[test]
    fn test_compute_signal_sell() {
        let prices = vec![107.0, 103.0, 100.0];
        let result = compute_signal(&prices).unwrap();
        assert_eq!(result.signal, Signal::Sell);
    }

    #[test]
    fn test_compute_signal_hold() {
        let prices = vec![100.0, 100.5, 100.2];
        let result = compute_signal(&prices).unwrap();
        assert_eq!(result.signal, Signal::Hold);
    }

    #[test]
    fn test_compute_signal_too_short() {
        assert!(compute_signal(&[100.0, 101.0]).is_none());
        assert!(compute_signal(&[]).is_none());
    }

    #[test]
    fn test_sma() {
        let prices = vec![10.0, 20.0, 30.0, 40.0, 50.0];
        assert_eq!(sma(&prices, 3), Some(40.0));
        assert_eq!(sma(&prices, 5), Some(30.0));
        assert!(sma(&prices, 10).is_none());
    }

    #[test]
    fn test_volatility() {
        let prices = vec![100.0, 100.0, 100.0];
        assert_eq!(volatility(&prices), Some(0.0));
        assert!(volatility(&[100.0]).is_none());
    }

    #[test]
    fn test_format_price() {
        assert_eq!(format_price(50000.0), "$50000.00");
        assert_eq!(format_price(142.5),   "$142.5000");
    }
}
