# Wuthering Waves Opti

A Python CLI tool for linking your Wuthering Waves account and optimizing your builds.

## Features

- **Account linking** — reads your account credentials directly from the game's local log file (no login required)
- **Convene history** — fetches your full pull history from Kuro's official API and shows pity counters per banner
- **Echo scoring** — scores your echo builds 0–100 using stat weights tuned per resonator archetype (crit DPS, ATK DPS, support, tank)

## Requirements

- Python 3.10+
- Wuthering Waves installed on the same machine

## Setup

```bash
git clone https://github.com/Ars-Deicide/WutheringWavesOpti.git
cd WutheringWavesOpti
pip install -r requirements.txt
```

## Usage

### Link your account

```bash
python main.py link
```

Before running this, open the **Convene History** screen inside the game at least once. The game writes the auth URL to its log file, which this tool reads.

### View convene history + pity

```bash
python main.py convene
```

Fetches pools 1–4 by default (Featured Resonator, Featured Weapon, Standard Resonator, Standard Weapon). Pass `--pools` to customize:

```bash
python main.py convene --pools 1,2
```

### Score your echo build

```bash
python main.py echoes Jiyan
```

Walks you through entering each echo's main stat and substats, then prints a per-echo score and an overall build grade (S / A / B / C / D).

Supported resonators: Jiyan, Calcharo, Carlotta, Changli, Camellya, Jinhsi, Encore, Danjin, Sanhua, Xiangli Yao, Verina, Shorekeeper, Baizhi, Yangyang, Rover, and more.

## How it works

Wuthering Waves displays your convene history as a webview inside the game. The URL for that webview — which includes your player ID and a session token — is written to a local log file. This tool reads that URL and queries the same Kuro API endpoint the game itself uses. No third-party servers involved; your data goes directly from Kuro's servers to your machine.

## Contributing

Pull requests are welcome!
