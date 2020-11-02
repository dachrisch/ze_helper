# Helper for ZE entries
Uses [Google Calendar](https://calendar.google.com/) entries to make [ze entries](https://ze.it-agile.de/)

## Features
all entries will become 
> 'laut Beschreibung (Intern)'

entries, except, when having the following attributes
* Event summary == 'Kurzarbeit' 
> 'Kurzarbeit (Intern)'

* Event summary == 'Krank'
> 'Krankheit (aufMUC-Zelle)'

* Event colorId == '4' (Flamingo)
> 'Durchführung (Workshops/Schulungen Pauschalpreis)'

* Event colorId == '6' (Tangerine)
> 'Vor-/Nachbereitung (Workshops/Schulungen Pauschalpreis)'
