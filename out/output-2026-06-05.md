# df-heylou-grok-extension — Output [CRUX-MK]
*Autonom aktiviert 2026-06-05T09:54:32.396145+00:00 | ollama-local/qwen2.5:14b-instruct*

# Dokumentation: df-heylou-grok-extension

## Grundlegende Informationen

- **Status:** SKELETON (v0.1.0-SKELETON), Tier: SKELETON-CONDITIONAL
- **Welle:** 39
- **K_0-Touch:** true, book_direct ist K_0-relevant.

### Beschreibung der Funktionen

**HeyLou als Sub-Funktion in Grok Function-Calling.**

Dieser Dark Factory integriert HeyLou als eine Unterfunktion in die Grok LL
LLM Plattform. Sie nutzt die HeyLou-API-Routinen für Hotel-Suche, Bewertung
Bewertungen, OTA-Vergleiche und direkte Buchungsanfragen.

### Warum?

Erweitert den Reach von HeyLou durch Integration mit der Grok-Userbasis und
und erhöht so die Verbreitung von HeyLou Services. Diese Erweiterung erford
erfordert `DF_HEYLOU_GROK_EXT_ENABLED=true`, `PHRONESIS_TICKET` und `GROK_A
`GROK_API_KEY` für den Real Mode Betrieb; in anderen Fällen wird ein Mock-M
Mock-Modus verwendet.

### Funktionsbeschreibung

1. **search_hotels(location, dates, preferences):**
   Hotel-Suche im HeyLou Travel Knowledge Graph.
   
2. **get_rates(hotel_id, date_range):** 
   PMS/RMS-Rates für ein spezifisches Hotel.
   
3. **compare_otas(hotel_id, dates):**
   Vergleich der Rates und Verfügbarkeiten von diversen OTAs (Booking.com, 
Expedia usw.).

4. **book_direct(hotel_id, room_type, guest, dates):**
   Direkte Buchungsanfrage ohne Kommission über HeyLou API.

5. **optimize_revenue(hotel_id):**
   Revenue-Optimierung für ein Hotel.

### Architektur

Die Grok LLM verarbeitet Anfragen und leitet sie an die `GrokExtension.hand
`GrokExtension.handle_function_call()` weiter, die dann entsprechende Funkt
Funktionen aus dem HeyLou API Backend aufruft. Hierfür werden JSON-Schemata
JSON-Schemata verwendet, um Tool-Declarations zu erstellen.

### Sandbox-Einstellungen

Für den Mock Modus ist `DF_HEYLOU_GROK_EXT_ENABLED=false`. Für den Real Mod
Mode Betrieb sind die Umgebungsvariablen `PHRONESIS_TICKET` und `GROK_API_K
`GROK_API_KEY` erforderlich.

### Test-Infrastruktur

```bash
pytest tests/ -v
```

## Integration mit anderen DFs (Cross-DF-Coupling)

Für Funktionsdefinitionen in Welle 36/37 Backend wird Lazy Import Stubs ver
verwendet, die sicherstellen, dass die Backends import-sicher sind.

Diese Dokumentation deckt den Aufbau und die Funktion der Dark Factory `df-
`df-heylou-grok-extension` ab, die eine Erweiterung des Reach von HeyLou du
durch Integration mit Grok LLM Plattformen ermöglicht.