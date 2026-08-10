from app.services.alert_service import check_watchlist_alerts

alerts = check_watchlist_alerts(
    telegram_id="8213190559",
    threshold=0.01
)

print("ALERTS:")

for alert in alerts:
    print(alert)