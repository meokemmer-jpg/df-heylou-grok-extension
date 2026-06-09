# df-heylou-grok-extension — PRODUKTION [CRUX-MK]
*2026-06-08T23:59:16.333831+00:00 | ollama-local/kemmer-14b-ctx8k*

# Dokumentation für df-heylou-grok-extension

## Grundlegende Informationen

- **Status:** VOLLSTAENDIG, Tier: GOLDCANDIDATE
- **Welle:** 39
- **K_0-Touch:** true, `book_direct` ist K_0-relevant.

### Warum?

Die Integration von HeyLou in die Grok LLM Plattform erweitert den Reach und die Reichweite der HeyLou Services durch die Nutzung der breiten Userbasis der Grok Plattform. Dies ermöglicht es, neue Kunden zu gewinnen und bestehende Kunden mit einem umfassenderen Angebot zu versorgen.

### Sandbox-Einstellungen

Für Entwicklung und Testzwecke ist das System in zwei Modi betrieben:

- **Mock-Modus:** `DF_HEYLOU_GROK_EXT_ENABLED=false` führt dazu, dass alle API-Aufrufe mit synthetischen Daten ausgeführt werden. Dies erleichtert die Fehlersuche und Testen ohne den Zugriff auf live-dienste zu benötigen.
  
- **Real-Modus:** `DF_HEYLOU_GROK_EXT_ENABLED=true`, zusammen mit `PHRONESIS_TICKET` und `GROK_API_KEY`. Diese Umgebungsvariablen stellen sicher, dass der Dark Factory realistische Daten und Services zur Verfügung stehen.

### Funktionsbeschreibung

1. **search_hotels(location, dates, preferences):**
   Dieser Funktion wird ein Suchbegriff für eine geografische Position (z.B. "New York"), einen Datumsbereich (z.B. ["2023-05-18", "2023-05-20"]) und persönliche Präferenzen übergeben, die das User-Profile reflektieren (z.B. Zimmerklasse, Wellnessangebote). Die Funktion durchsucht den HeyLou Travel Knowledge Graph für passende Hotels und gibt eine Liste von Hotelvorschlägen zurück.

   **Beispiel-Aufruf:**
   ```python
   search_hotels("New York", ["2023-05-18", "2023-05-20"], {"room_class": "Deluxe"})
   ```

2. **get_rates(hotel_id, date_range):** 
   Diese Funktion erfragt die Preise und Verfügbarkeiten für ein spezifisches Hotel (`hotel_id`) in einem bestimmten Datumsbereich (`date_range`). Sie verwendet den df-pms-mews-adapter zur Kommunikation mit dem PMS/RMS des Hotels.

   **Beispiel-Aufruf:**
   ```python
   get_rates("12345", ["2023-06-05", "2023-06-07"])
   ```

3. **compare_otas(hotel_id, dates):**
   Diese Funktion vergleicht die Preise und Verfügbarkeiten für ein Hotel (`hotel_id`) über verschiedene Online Travel Agenturen (OTAs) wie Booking.com, Expedia usw. Sie bietet dem Nutzer eine Übersicht der besten Angebote.

   **Beispiel-Aufruf:**
   ```python
   compare_otas("12345", ["2023-06-05"])
   ```

4. **book_direct(hotel_id, room_type, guest, dates):**
   Mit dieser Funktion kann ein Hotel direkt über den HeyLou API Service gebucht werden, ohne zusätzliche Kommissionen zu entstehen. Es benötigt die `hotel_id`, eine Beschreibung des Zimmertyps (`room_type`), Angaben zum Gast (z.B. Name und Kontaktinformationen) sowie die Buchungsdaten.

   **Beispiel-Aufruf:**
   ```python
   book_direct("12345", "Single Room", {"name": "John Doe", "email": "john.doe@example.com"}, ["2023-06-05"])
   ```

5. **optimize_revenue(hotel_id):**
   Diese Funktion bietet eine Revenue-Optimierung für ein Hotel (`hotel_id`). Sie analysiert die aktuellen Buchungen und empfiehlt Anpassungen an den Preis oder die Verfügbarkeit, um maximale Gewinne zu erzielen.

### Architektur

1. **Grok LLM:** Der Grok Language Model Management System verarbeitet alle eingehenden User-Anfragen und richtet sie als `functionCall` an unsere Extension, df-heylou-grok-extension.
   
2. **df-heylou-grok-extension.handle_function_call():** Diese Methode leitet die Anfrage an das entsprechende Backend-Modul weiter (z.B. df-pms-mews-adapter für `get_rates`). Es gibt Mocks für alle Funktionen in Entwicklungsmodus (`DF_HEYLOU_GROK_EXT_ENABLED=false`).

3. **Backend Integration:** Für jede Funktionsaufruf werden spezielle Adapter verwendet, die Daten aus verschiedenen Quellen (z.B. Hotelsystems) extrahieren und diese an den Grok LLM zurückgeben.

### Sandbox-Architektur

Die Architektur besteht aus folgenden Hauptkomponenten:

- **Grok LLM:** Verarbeitet Anfragen und leitet sie in Form von `functionCall` an die Erweiterung.
- **df-heylou-grok-extension.handle_function_call()**: Diese Methode handhabt Funktionen wie `search_hotels`, `get_rates`, `compare_otas`, `book_direct` und `optimize_revenue`. Sie verarbeitet JSON-Schemata für Tool Declarations, um sicherzustellen, dass die Daten korrekt formatiert sind.
- **AuditLogger (HMAC-SHA256 JSONL)**: Ein Logger, der jede Funktion aufnimmt und sie nach Standards des HMAC-SHA256 speichert. Dies ist wichtig zur Überwachung und Sicherheit.

### Integration mit anderen DFs (Cross-DF-Coupling)

Für die Funktionsdefinitionen in Welle 36/37 Backend wird Lazy Import Stubs verwendet, um sicherzustellen, dass Backends import-sicher sind und keine Fehler während der Entwicklung auftreten. Dies verhindert auch unnötige Abhängigkeiten von unvollständigen oder noch nicht implementierten Modulen.

### Test-Infrastruktur

Die Testinfrastruktur ist in einem Docker-Build-Container integriert, um sicherzustellen, dass alle Tests einheitlich durchgeführt werden können. Die Tests werden mithilfe der pytest-Bibliothek ausgeführt:

```bash
pytest tests/ -v
```

Diese Kommandozeile führt eine Reihe von Tests aus und liefert detaillierte Ergebnisse.

### Sandbox-Default

Folgende Umgebungsvariablen bestimmen das Verhalten des Systems im Sandbox-Modus:

- `DF_HEYLOU_GROK_EXT_ENABLED=false`: Betreibt den System im Mock Modus.
  
- `PHRONESIS_TICKET`: Ist erforderlich für das Zugriff auf die realen Services. Es ist ein Sicherheitsticket, das Authentifizierung ermöglicht.

- `GROK_API_KEY`: Eine API-Schlüssel für die Kommunikation mit der Grok LLM Plattform.

### Sandbox-Architektur

Die Architektur des Sandboxesystems sieht folgendermaßen aus:

```
Grok-LLM → functionCall → df-heylou-grok-extension.handle_function_call()
                              ├── search_hotels    → mock | df-heylou-travel-domain
                              ├── get_rates        → mock | df-pms-mews-adapter
                              ├── compare_otas     → mock | df-ota-booking-adapter
                              ├── book_direct      → mock | df-heylou-travel-domain (K_0)
                              └── optimize_revenue → mock | W40-Stub
                              ↓
                          AuditLogger (HMAC-SHA256 JSONL)
```

### Sandbox-Monitore

Für den Überblick über die Performance und das Verhalten des Systems sind folgende Monitore implementiert:

- **Performance-Monitoring:** Mit Prometheus und Grafana kann man in Echtzeit die Performance-Metriken anzeigen.
  
- **Log-Auswertung:** Elasticsearch, Kibana kombiniert mit Filebeat sammelt und analysiert Logs.

### Sandbox-Deployment

Für das Deployment im Sandbox-Modus wird ein LaunchAgent verwendet:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kemmer.df-heylou-grok-extension</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/make/Projects/dark-factories/df-heylou-grok-extension/run_script.py</string>
    </array>
    <key>StartInterval</key>
    <integer>7200</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Sandbox-Tests

Die Tests sind unter `tests/` zu finden und können über die Kommandozeile ausgeführt werden:

```bash
pytest tests/ -v
```
Dies führt alle in der `tests/` Datei definierten Testfälle durch.

## Fazit

Die Integration von HeyLou in die Grok LLM Plattform ist eine kraftvolle Erweiterung, die den Reach von HeyLou erheblich erhöht. Durch die Bereitstellung einer umfassenden Suite von Funktionen für Hotelbuchungen und -bewertungen wird es den Nutzern ermöglicht, ein breites Spektrum an Dienstleistungen ohne Kommission zu nutzen.