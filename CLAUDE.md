# Travelmap Robert

- `index.html`: de pagina (opmaak, code en het ontgrendelscherm).
- De data is versleuteld. In de repo staan alleen `data.enc`, `keys.json` en `share/*.json`.
  De leesbare `data.js` staat in `.gitignore` en mag NOOIT gecommit worden (repo is openbaar).
  Ook persoonlijke data (plekken, reizen, `MANUAL`) hoort in `data.js`, niet in `index.html`.
- Werken met de data: `tools/travelcrypt.py` met het wachtwoord in `TRAVEL_PW`
  (vraag het aan Robert, schrijf het nergens op in de repo).
  - Data bijwerken: `decrypt` → `data.js` aanpassen → `encrypt`. Deellinks blijven werken.
  - Deellink maken: Robert doet dit zelf met de knop "Deellink maken (7 dagen)" in de pagina
    (schrijft via de GitHub-API met een fine-grained token dat alleen op zijn apparaat staat).
    Via de terminal kan ook: `share 7 "naam"` → commit + push van `share/<id>.json`, geef Robert de link.
  - Deellinks kunnen ook een deel van de data bevatten (reis, land of jaren): dan staat er naast
    `share/<id>.json` een `share/<id>.enc` met alleen die data, versleuteld met de deelsleutel.
    Het label en de deelsleutel staan versleuteld met DK in `meta`, zodat Robert zijn links kan beheren.
  - Wachtwoord wijzigen: `passwd NIEUW`.
- Verlopen deellinks worden elk uur verwijderd door `.github/workflows/deellinks-opruimen.yml`.
  De pagina controleert de vervaldatum ook zelf.
- Versienummer staat in `index.html` als `const VERSION = "JJ.MM.N"`.
  Verhoog het bij elke wijziging: JJ = jaar, MM = maand, N = volgnummer binnen die maand
  (begint weer bij 1 in een nieuwe maand). Bijvoorbeeld 26.10.1 → 26.10.2 → 26.11.1.
- De datum "Foto's t/m" wordt automatisch berekend uit de laatste fotodatum in de data.
