# 🎮 Game Achievement Management System

> **Achievement Tracking & Player Progression Platform**  
> A modular, RESTful backend service built with **Django** and **Django REST Framework** to manage video game catalogs, track unlockable achievements, and power a gamified player leveling and experience (EXP) progression engine.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Data Dictionary](#data-dictionary)
- [REST API Specification](#-rest-api-specification)
- [Getting Started](#-getting-started)

---

## 🌟 Overview

The **Game Achievement Management System** (`achievement_tracking`) provides a centralized platform for tracking player interactions with games, milestone achievements, and profile progression. 

By separating domains into distinct Django applications, the platform offers an extensible and normalized database architecture:
- **Game Catalogs**: Organize games by publisher and genre.
- **Achievement Engine**: Define discrete achievements for each game, each granting experience points (`exp_value`).
- **Player Profiles & Leveling**: Custom user authentication tied to a multi-tiered leveling system where players advance as they earn achievements.
- **Engagement Tracking**: Associative tracking for player game libraries and time-stamped achievement unlocks.

---

## 🚀 Key Features

- **Custom Player Authentication**: Extends Django's `AbstractUser` to create `PlayerProfiles`, associating each player directly with rank and level progression.
- **Gamified Level Progression**: Dynamic leveling table (`Levels`) mapping required EXP thresholds to cosmetic rank titles (e.g., Novice, Veteran, Master).
- **Game & Achievement Catalog**: Full support for cataloging games and assigning game-specific achievements with custom EXP values and descriptions.
- **Player Library (`PlayerGames`)**: Junction tracking of which games players have in their personal library.
- **Achievement Unlocks (`PlayerAchievements`)**: Real-time logging of achievement unlocks complete with acquisition timestamps (`acquired_date`).
- **RESTful API Architecture**: Ready for frontend integration (e.g., Vue, React) via Django REST Framework serializers and viewsets.

---

### Data Dictionary

#### 1. `levels`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique level tier identifier |
| `number` | `IntegerField` | Required | Numeric level (e.g., `1`, `2`, `10`) |
| `exp_required` | `IntegerField` | Required | Cumulative EXP threshold to attain this level |
| `title` | `CharField(50)` | Required | Rank title (e.g., `"Novice"`, `"Grandmaster"`) |

#### 2. `player_profiles`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique player identifier |
| `username` | `CharField(100)`| Unique, Required | Player handle / username |
| `password` | `CharField(100)`| Required | Hashed authentication credential |
| `email` | `EmailField` | Optional | Player contact email |
| `first_name` | `CharField(100)`| Optional | Player's given name |
| `last_name` | `CharField(100)`| Optional | Player's surname |
| `level` | `ForeignKey` | `levels.Levels`, `ON_DELETE=PROTECT` | Current level rank of the player |
| `created_at` | `DateTimeField`| Auto add now | Profile creation timestamp |
| `updated_at` | `DateTimeField`| Auto update now | Last profile update timestamp |

#### 3. `games`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique game identifier |
| `title` | `CharField(100)`| Required | Name of the video game |
| `publisher` | `CharField(100)`| Required | Studio or company publishing the title |
| `genre` | `CharField(100)`| Required | Categorical classification (e.g., RPG, FPS) |

#### 4. `achievements`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique achievement identifier |
| `name` | `CharField(100)`| Required | Achievement title (e.g., "First Blood") |
| `description` | `TextField` | Required | Instructions or condition to unlock |
| `exp_value` | `IntegerField` | Required | Experience point reward granted |
| `game_id` | `ForeignKey` | `games.Games`, `ON_DELETE=PROTECT` | Associated game |

#### 5. `player_games`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique entry identifier |
| `player_id` | `ForeignKey` | `PlayerProfiles`, `ON_DELETE=PROTECT` | The player who owns/plays the game |
| `game_id` | `ForeignKey` | `games.Games`, `ON_DELETE=PROTECT` | The game belonging to the player |

#### 6. `player_achievements`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `AutoField` | Primary Key | Unique unlock record identifier |
| `player_id` | `ForeignKey` | `PlayerProfiles`, `ON_DELETE=PROTECT` | Player who earned the achievement |
| `achievement_id` | `ForeignKey` | `achievements.Achievements`, `ON_DELETE=PROTECT`| The unlocked achievement |
| `acquired_date` | `DateField` | Required | Calendar date when unlocked |

---

## 🔌 REST API Specification

The service exposes RESTful endpoints for CRUD operations and query filters across all domains:

### Player Profiles & Authentication
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/register/` | Register a new player account |
| `POST` | `/api/login/` | Authenticate and obtain session/token |

### Levels & Progression
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/levels/` | List all level thresholds and rank titles |
| `POST` | `/api/levels/` | Create a new level tier (Admin) |

### Games Catalog
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/games/` | List all cataloged games |
| `POST` | `/api/games/` | Add a new game to the catalog |

### Achievements
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/achievements/` | List all achievements (filterable by `game_id`) |
| `POST` | `/api/achievements/` | Create a new achievement for a game |

### Player Games (Library)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/player-games/` | List player game associations (filterable by `player_id`) |
| `POST` | `/api/player-games/` | Add a game to a player's library |

### Player Achievements (Unlocked)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/player-achievements/` | List all unlocked achievements |
| `POST` | `/api/player-achievements/` | Record an achievement unlock for a player |

---

## 🛠 Getting Started

### Prerequisites

- [Python 3.14+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [PostgreSQL](https://www.postgresql.org/)

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Sodayooo-dev/achievement_tracking.git
   cd achievement_tracking
   ```

2. **Create and Activate Virtual Environment**
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Database Migrations

Apply the existing migrations to build the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```
Start the Development Server
   ```bash
   python manage.py runserver
   ```