# Python 2D Engine – Pong

Eine kleine 2D-Engine in Python mit OpenGL-Rendering, GLFW-Fensterverwaltung, Tastatureingabe, Kamera, JSON-Szenen und einem Entity-Component-System (ECS). Als aktuelles Beispielspiel startet das Projekt ein lokales Zwei-Spieler-Pong.

Das Projekt ist bewusst überschaubar gehalten: Die Engine stellt allgemeine Bausteine bereit, während `game/pong/game.py` die eigentlichen Pong-Regeln implementiert. Dadurch lässt sich nachvollziehen, wie aus Entities, Komponenten und wenigen Spielsystemen ein vollständiges kleines Spiel entsteht.

## Aktueller Funktionsumfang

Das aktuelle `main.py` startet ein Pong-Fenster mit einer virtuellen Spielfläche von 800 × 600 Einheiten. Enthalten sind:

- zwei lokal steuerbare Schläger,
- ein Ball mit horizontaler und vertikaler Bewegung,
- Reflexion an der oberen und unteren Spielfeldkante,
- Schlägerkollisionen mit trefferpunktabhängigem Spin,
- Punktestand als Sieben-Segment-Anzeige,
- Startanzeige für die erste Runde,
- Siegeranzeige nach fünf Punkten,
- Neustart des Matches mit `R`,
- Beenden nach dem Sieg mit `Esc` oder `Q`,
- Rendering aller Spiel- und UI-Elemente als farbige Quads.

## Schnellstart unter Windows

PowerShell im Projektverzeichnis öffnen:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Wenn `.venv` bereits existiert, kann die erste Zeile übersprungen werden. Die virtuelle Umgebung muss nicht aktiviert werden, da die Befehle den Python-Interpreter darin direkt aufrufen.

Alternativ mit aktivierter Umgebung:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Beim Start wird ein Fenster mit dem Titel **Pong** in der Größe 800 × 600 geöffnet. Zum Beenden kann das Fenster geschlossen werden. Die Anwendung benötigt eine Desktop-Umgebung und einen Grafiktreiber mit OpenGL 3.3 oder höher.

## Pong spielen

| Taste | Aktion |
| --- | --- |
| `W` | Linken Schläger nach oben bewegen |
| `S` | Linken Schläger nach unten bewegen |
| Pfeiltaste `↑` | Rechten Schläger nach oben bewegen |
| Pfeiltaste `↓` | Rechten Schläger nach unten bewegen |
| `Space` | Ball starten bzw. eine neue Runde beginnen |
| `R` | Nach Spielende Match auf 0:0 zurücksetzen |
| `Esc` oder `Q` | Nach Spielende das Fenster schließen |
| Fenster-Schließen-Schaltfläche | Anwendung beenden |

Zu Beginn befindet sich der Ball in der Spielfeldmitte und bewegt sich erst nach `Space`. Nach jedem Punkt wird der Ball ebenfalls in die Mitte zurückgesetzt. Die nächste Runde beginnt erneut mit `Space`.

Ein Match endet, sobald eine Seite fünf Punkte erreicht. Während des Endzustands werden der Sieger (`LINKS` oder `RECHTS`) und die Hinweise `R NEUSTART` sowie `ESC BEENDEN` angezeigt.

## Pong-Regeln und Spielwerte

| Wert | Aktuelle Implementierung |
| --- | --- |
| Spielfeld | 800 × 600 Einheiten |
| Linker Schläger | Mittelpunkt `(32, 300)`, Größe 16 × 96 |
| Rechter Schläger | Mittelpunkt `(768, 300)`, Größe 16 × 96 |
| Ball | Mittelpunkt `(400, 300)`, Größe 16 × 16 |
| Schlägergeschwindigkeit | 360 Einheiten pro Sekunde |
| Ballgeschwindigkeit | 330 Einheiten pro Sekunde |
| Gewinnbedingung | 5 Punkte |
| Linker Schläger | Cyanblau, über `W`/`S` gesteuert |
| Rechter Schläger | Orange, über die Pfeiltasten gesteuert |
| Ball | Weiß |
| Spielfeldmarkierungen | Dunkle Mittellinie und obere/untere Markierungen |

Beim Start wird die horizontale Ballrichtung zufällig nach links oder rechts gewählt. Die vertikale Richtung erhält einen zufälligen Anteil zwischen `-0.75` und `0.75`; anschließend wird der Richtungsvektor normalisiert und mit 330 multipliziert.

Der Ball wird pro Update bewegt. Wenn er die obere oder untere Kante erreicht, wird seine vertikale Geschwindigkeit gespiegelt und seine Position an der Kante korrigiert. Bei einem Treffer mit dem linken oder rechten Schläger wird die horizontale Richtung gespiegelt. Zusätzlich wird ein vertikaler Spin abhängig vom Abstand zwischen Ballmitte und Schlägermitte addiert. Danach wird die Gesamtgeschwindigkeit erneut auf `BALL_SPEED` normalisiert.

Ein Punkt wird vergeben, wenn der Ball das Spielfeld vollständig links oder rechts verlässt. Der Ball gilt dabei erst außerhalb des Feldes, wenn seine Position weiter als eine Ballbreite über die entsprechende Grenze hinausgelaufen ist.

## Ablauf des Spiels

Die Zustandslogik in `Game.update()` lässt sich so zusammenfassen:

```text
Tastenzustände lesen
        |
        v
Ist das Match beendet? -- ja --> R: Neustart / Q oder Esc: Fenster schließen
        |
       nein
        v
Schläger bewegen und an den Rändern begrenzen
        |
        v
Runde gestartet? ------- nein --> bei Space Ball starten, sonst warten
        |
       ja
        v
Ball bewegen, Rand- und Schlägerkollision prüfen
        |
        v
Ball im Tor? --> Punkt vergeben --> Runde zurücksetzen oder Match beenden
```

Der Ballzeitschritt wird in `_move_ball()` auf maximal `0.05` Sekunden begrenzt. Das verhindert, dass ein ungewöhnlich großer Frame-Zeitschritt die einfache diskrete Kollisionserkennung unnötig instabil macht.

## Aufbau des Pong-Beispiels

### Einstiegspunkt

`main.py` erzeugt das Spiel mit den Abmessungen 800 × 600 und übergibt es an `Application`:

```python
game = Game(800, 600)

app = Application(
    game,
    width=800,
    height=600,
    title="Pong",
)
app.run()
```

Die `Application` verwendet `game.world_width` und `game.world_height` als virtuelle Rendererauflösung. Damit stimmen Projektion, Kamera und Spielkoordinaten mit der Pong-Spielfläche überein.

### Szene

`game/pong/assets/scenes/main.json` enthält die drei statischen Kern-Entities:

```text
Linker Schläger  -> Transform + QuadRenderable + LeftPlayer
Rechter Schläger -> Transform + QuadRenderable + RightPlayer
Ball             -> Transform + Velocity + QuadRenderable + BallSpawn
```

Die Szene definiert Position, Größe, Farbe, Zeichenreihenfolge und beim Ball zusätzlich den initialen Geschwindigkeitsvektor. Die Runtime-Logik übernimmt anschließend die Bewegung und alle Änderungen an diesen Komponenten.

Die spielespezifischen Tags werden in `game/pong/components.py` als leere Dataclasses definiert:

```python
@dataclass
class LeftPlayerTag:
    pass

@dataclass
class RightPlayerTag:
    pass

@dataclass
class BallSpawnTag:
    pass
```

Im Konstruktor des Pong-Spiels werden die drei Namen über `ComponentRegistry.register()` beim SceneLoader registriert. Der Engine-Kern muss dadurch keine Pong-spezifischen Komponenten kennen.

### Spielzustand

`Game` hält den veränderlichen Pong-Zustand direkt als Attribute:

| Attribut | Bedeutung |
| --- | --- |
| `left_score` | Punkte der linken Seite |
| `right_score` | Punkte der rechten Seite |
| `round_started` | Gibt an, ob sich der Ball bewegt |
| `game_over` | Match ist beendet |
| `winner` | Siegertext `LINKS` oder `RECHTS` |
| `ball_velocity` | `Velocity`-Komponente des Balls |
| `_dynamic_ui` | Entities der dynamisch neu erzeugten Punkt-/Statusanzeige |
| `_raw_previous` | Vorheriger Zustand von `R`, `Q` und `Escape` |

Die statischen Spielfeldmarkierungen werden einmal in `_build_static_ui()` erzeugt. Die dynamische Anzeige wird in `_refresh_ui()` bei jedem Punkt und bei jedem Zustandswechsel neu aufgebaut. Alte dynamische Entities werden vorher aus der ECS-World entfernt.

### UI ohne separates UI-System

Pong besitzt derzeit kein eigenes Text- oder UI-Framework. Stattdessen werden alle Anzeigeelemente als normale Entities mit `Transform` und `QuadRenderable` erzeugt:

- Der Punktestand wird aus sieben Segmenten zusammengesetzt.
- Statusmeldungen werden über kleine Pixelmuster gezeichnet.
- Ein höherer `z_index` legt die Anzeige über Spielfeld und Schläger.

Das zeigt eine einfache Möglichkeit, mit der vorhandenen Quad-Pipeline bereits HUD-Elemente darzustellen. Für ein größeres Spiel wäre ein eigenes Text-/UI-System sinnvoller.

## Engine-Architektur

### Application Loop

`engine/application.py` übernimmt die wiederkehrende Hauptschleife:

```text
Zeit messen
  -> GLFW-Ereignisse abfragen
  -> Eingabe aktualisieren
  -> game.update(dt, input)
  -> Framebuffer-Größe abfragen
  -> Renderer-Viewport anpassen
  -> Frame löschen
  -> game.render(renderer, resources)
  -> Buffer tauschen
```

`dt` ist die seit dem letzten Frame verstrichene Zeit in Sekunden. Die Spielbewegung wird dadurch framerate-unabhängig berechnet.

### Entity-Component-System

`engine/ecs/world.py` verwaltet fortlaufende Integer-Entity-IDs und Komponenten nach Typ. Eine Entity kann beliebig viele verschiedene Komponententypen besitzen, aber höchstens eine Komponente pro Typ. Das Hinzufügen einer zweiten Komponente desselben Typs ersetzt die erste.

Beispiel:

```python
world = World()
entity = world.create_entity()

world.add_component(
    entity,
    Transform(position=Vector2(10.0, 20.0)),
)
world.add_component(
    entity,
    Velocity(Vector2(100.0, 0.0)),
)

movement_system(world, dt=0.5)
```

Die Position beträgt danach `(60.0, 20.0)`. Abfragen liefern zuerst die Entity-ID und danach die Komponenten in der Reihenfolge der Anfrage:

```python
for entity, transform, velocity in world.query(Transform, Velocity):
    print(transform.position.x, transform.position.y)
```

Leere Tags werden verwendet, wenn eine Entity nach ihrer Rolle gefiltert werden soll. Pong fragt zum Beispiel nach `LeftPlayerTag` und `Transform`, um den linken Schläger zu finden.

### Engine-Komponenten

| Komponente | Zweck |
| --- | --- |
| `Transform` | Position, vollständige Größe und Rotation eines Objekts |
| `Velocity` | Bewegungsvektor in Weltkoordinaten |
| `QuadRenderable` | Farbe, optionale Textur und `z_index` |
| `Parent` | Hierarchische Beziehung zwischen Entities |
| `PlayerSpawn` | Marker für einen Spielerstart in Szenen |

`Transform.position` bezeichnet die Mitte eines Quads. `Transform.scale` speichert die vollständige Breite und Höhe. Weltkoordinaten wachsen nach rechts auf der X-Achse und nach unten auf der Y-Achse. Rotationen werden in Radiant angegeben.

### Bewegungssystem

`engine/ecs/systems/movement.py` bewegt Entities mit `Transform` und `Velocity` nach:

```text
position = position + velocity * dt
```

Pong verwendet dieses generische System nicht für den Ball, da Ballbewegung, Randreflexion, Schlägerkollision und Punktvergabe in einem kontrollierten Ablauf zusammengehören. Die `Velocity`-Komponente des Balls wird dennoch im ECS gespeichert und von Pong direkt aktualisiert.

### Rendering

`engine/renderer.py` zeichnet ein wiederverwendbares OpenGL-Quad. Der Renderer:

- verwendet OpenGL-Shader mit `#version 330 core`,
- lädt Vertex- und Indexdaten einmal in GPU-Puffer,
- unterstützt Position, Größe und Rotation,
- zeichnet RGBA-Farben oder optionale Texturen,
- aktiviert Alpha-Blending,
- passt den Viewport an das Seitenverhältnis der virtuellen Auflösung an.

`quad_render_system()` fragt alle Entities mit `Transform` und `QuadRenderable` ab, sortiert nach `z_index`, löst bei Bedarf Texturen über den `ResourceManager` auf und ruft anschließend `renderer.render()` auf.

Pong nutzt nur Farbwerte. Die Textur-Unterstützung gehört trotzdem zum Engine-Kern und wird von anderen Szenen bzw. dem älteren Shooter-Code vorbereitet.

### Kamera und Koordinaten

`Camera2D` wandelt Weltpositionen in Bildschirmpositionen um. Pong hält die Kamera bei ihrer Standardposition, weil die gesamte Welt exakt der sichtbaren Spielfläche entspricht. Die Kamera ist dennoch Teil der allgemeinen `Application`-/`Renderer`-Schnittstelle und wird vom Spiel bereitgestellt.

### Eingabe

`engine/input.py` speichert pro Frame den aktuellen und den vorherigen Tastaturzustand:

- `is_key_down(key)` bleibt wahr, solange eine Taste gedrückt ist.
- `was_key_pressed(key)` ist nur beim Übergang von nicht gedrückt zu gedrückt wahr.

Pong verwendet den normalen Input-Zustand für Schläger und `Space`. Für `R`, `Q` und `Escape` wird in `_raw_keys()` zusätzlich direkt GLFW abgefragt. Diese Tasten werden nur benötigt, wenn das Match bereits beendet ist.

Die Engine kennt die Enum-Werte `UP` und `DOWN`. Die GLFW-Zuordnung für die Pfeiltasten wird in `game/pong/game.py` ergänzt:

```python
KEY_MAP[Key.UP] = glfw.KEY_UP
KEY_MAP[Key.DOWN] = glfw.KEY_DOWN
```

## Szenen und ComponentRegistry

Szenen sind JSON-Dateien mit einer `entities`-Liste. Jede Entity enthält ein `components`-Objekt:

```json
{
  "entities": [
    {
      "components": {
        "Transform": {
          "position": [400.0, 300.0],
          "scale": [16.0, 16.0],
          "rotation": 0.0
        },
        "Velocity": {
          "value": [0.0, 0.0]
        },
        "QuadRenderable": {
          "color": [1.0, 1.0, 1.0, 1.0],
          "z_index": 1
        }
      }
    }
  ]
}
```

`ComponentRegistry` enthält Loader für die Engine-Komponenten `Transform`, `QuadRenderable`, `Velocity`, `Parent` und `PlayerSpawn`. Spiele können zusätzliche Loader registrieren, wie Pong es für `LeftPlayer`, `RightPlayer` und `BallSpawn` tut.

Der `SceneLoader` arbeitet in zwei Durchläufen:

1. Runtime-Entities werden erzeugt und optionale JSON-IDs registriert.
2. Komponenten werden aus den JSON-Daten erzeugt und an die Entities angehängt.

Parent-Referenzen werden dabei von einer lesbaren Scene-ID auf eine Runtime-Entity-ID aufgelöst. Doppelte Scene-IDs und unbekannte Parent-IDs führen zu `ValueError`.

## Kollisionen

`engine/collision.py` verwendet achsenparallele Bounding Boxes (AABB). Die Prüfung basiert auf Position und vollständiger Größe des `Transform`; Rotation wird ignoriert. Rechtecke, die sich nur an einer Kante berühren, gelten nicht als Kollision.

Diese einfache Kollision ist für Pong geeignet, weil Ball und Schläger nicht rotiert werden. Die Prüfung ist diskret: Der Ball wird bewegt und danach an seiner neuen Position geprüft. Ein echtes Swept-Collision-System, das die gesamte Flugstrecke innerhalb eines Frames untersucht, ist nicht vorhanden.

## Ressourcen und Texturen

`ResourceManager` cached geladene Texturen nach ihrem Pfad. `Texture` lädt Bilddateien über Pillow als RGBA und erstellt daraus OpenGL-Texturen mit Nearest-Neighbor-Filterung. Ressourcen werden beim Beenden vor dem OpenGL-Kontext freigegeben.

Pong benötigt keine Bilddateien. Im Repository liegen dennoch `game/assets/tile_0000.png` bis `tile_0015.png` als vorhandene Textur-Assets für andere bzw. ältere Beispielstände.

## Projektstruktur

```text
.
├── main.py                         # Startet das aktuelle Pong-Spiel
├── requirements.txt                # Laufzeitabhängigkeiten
├── requirements-dev.txt            # Entwicklungsabhängigkeiten
├── pyproject.toml                  # pytest-, mypy-, pyright- und Coverage-Konfiguration
├── engine/
│   ├── application.py              # Hauptschleife und Game/Renderer-Integration
│   ├── window.py                   # GLFW-Fenster und Tastenabfrage
│   ├── input.py                    # aktuelle/vorherige Tastenzustände
│   ├── key.py                      # Engine-Tasten-Enum
│   ├── renderer.py                 # OpenGL-Shader und Quad-Rendering
│   ├── texture.py                  # Bild- und GPU-Texturen
│   ├── resource_manager.py         # Textur-Cache und Lebenszyklus
│   ├── camera.py                   # Welt-zu-Bildschirm-Umrechnung
│   ├── scene.py                    # Scene-Container
│   ├── scene_loader.py             # JSON-Szenen laden
│   ├── collision.py                # AABB-Kollisionen
│   ├── vector2.py                  # 2D-Vektorrechnung
│   ├── timer.py                    # Timer-Grundlage
│   └── ecs/
│       ├── world.py                # Entity-/Komponentenverwaltung
│       ├── hierarchy.py             # Entity-Hierarchien
│       ├── transform_resolver.py    # Welttransformationen
│       ├── components/              # Transform, Velocity, Parent usw.
│       └── systems/                 # Movement und Quad-Rendering
├── game/
│   ├── pong/
│   │   ├── game.py                 # Pong-Regeln, Ball, Score und UI
│   │   ├── components.py           # Pong-Tags
│   │   └── assets/scenes/main.json # Pong-Szene
│   ├── wave_shooter/               # älterer ausgelagerter Shooter-Code
│   ├── arkanoid/                   # derzeit nur Paketmarker
│   └── assets/                     # vorhandene Textur- und Szenen-Assets
└── tests/                          # Engine- und ältere Gameplay-Tests
```

## Tests

Die Tests werden aus dem Projektstamm ausgeführt:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Der aktuelle Testlauf zeigt derzeit:

- **68 Tests erfolgreich** für Engine, ECS, Renderer-Hilfslogik, Szenenloader, Eingabe und ältere Gameplay-Funktionen.
- **2 Importfehler** in `tests/test_game.py` und `tests/test_game_systems.py`.

Die beiden Fehler entstehen, weil diese Tests noch `game.components`, `game.game` und `game.systems` importieren, während die zugehörigen älteren Dateien inzwischen unter `game/wave_shooter/` liegen. Das ist eine veraltete Testreferenz und kein Fehler des aktuellen Pong-Imports. Pong besitzt im aktuellen Stand noch keine eigene Testdatei.

Für Pong wären insbesondere folgende Tests sinnvoll:

- Ball startet erst bei `Space`.
- Schläger bleiben innerhalb der Spielfeldhöhe.
- Ball reflektiert an oberer und unterer Kante.
- Ball reflektiert am richtigen Schläger.
- Trefferpunkt erzeugt den erwarteten Spin.
- Linke und rechte Seite erhalten beim Verlassen des Balls den korrekten Punkt.
- Bei fünf Punkten wird der richtige Sieger gesetzt.
- `R` setzt das Match zurück und `Q`/`Escape` schließen das Fenster.

## Bekannte Einschränkungen

- Pong ist ausschließlich für zwei lokale Spieler ausgelegt und enthält keine Computer-Gegner-KI.
- Es gibt keinen Sound, keine Musik, keine Partikel und kein dauerhaft gespeichertes Highscore-System.
- Die Punkt- und Textanzeige wird aus Quads aufgebaut; ein echtes Font-/UI-System existiert noch nicht.
- Die Kollisionserkennung ist diskret und berücksichtigt keine Rotationen.
- Die Kamera wird im Pong-Spiel nicht dynamisch bewegt, da das Spielfeld vollständig in den Viewport passt.
- Das Repository enthält ältere Wave-Shooter-Dateien und Tests, deren Importpfade nach der Umstrukturierung nicht vollständig angepasst wurden.
- Die Engine setzt OpenGL 3.3 und eine funktionierende Desktop-Fensterumgebung voraus.
- Es gibt keinen Editor und keine automatische Asset-Import-Pipeline.

## Mögliche nächste Schritte

Naheliegende Erweiterungen wären:

1. Pong-spezifische Unit-Tests ergänzen.
2. Die alten Shooter-Tests auf `game.wave_shooter` umstellen oder bewusst entfernen.
3. Ein generisches Text-/UI-System aus der aktuellen Quad-basierten Anzeige entwickeln.
4. Ein Action-Mapping einführen, damit Pfeiltasten nicht im Spielmodul direkt in `KEY_MAP` eingetragen werden müssen.
5. Soundeffekte, Pause und Match-Einstellungen ergänzen.
6. Eine Swept-Collision-Variante für schnelle Objekte hinzufügen.
7. Einen zentralen Spielauswahl-Einstiegspunkt für Pong, Shooter und zukünftige Beispiele bereitstellen.

## Screenshots

Das aktuelle Projekt ist ein lokales OpenGL-Desktopspiel. In dieser Arbeitsumgebung wurde kein verifizierter Fensterscreenshot als Datei abgelegt; deshalb enthält die README keine künstlich erzeugte oder unbestätigte Aufnahme. Ein geeigneter Screenshot sollte den Startzustand mit `SPACE START`, den cyanblauen linken Schläger, den orangenen rechten Schläger, den weißen Ball, die Mittellinie und den Punktestand zeigen.

## Lizenz

Siehe [LICENSE](LICENSE). Das Projekt steht unter der GNU General Public License, Version 3.
