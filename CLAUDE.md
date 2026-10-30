# Travelmap Robert

- `index.html`: de pagina (opmaak en code). `data.js`: kaartdata, landen, fotopunten en reizen.
- Versienummer staat in `index.html` als `const VERSION = "JJ.MM.N"`.
  Verhoog het bij elke wijziging: JJ = jaar, MM = maand, N = volgnummer binnen die maand
  (begint weer bij 1 in een nieuwe maand). Bijvoorbeeld 26.10.1 → 26.10.2 → 26.11.1.
- De datum "Foto's t/m" wordt automatisch berekend uit de laatste fotodatum in `data.js`.
