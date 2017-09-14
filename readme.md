# pr0miumadapter
Erlaubt es, den [pr0miner](http://miner.pr0gramm.com/) mit optimierten
Moneropoolclients zu verwenden. Natürlich auf eigene Gefahr.
Dient außerdem als python asyncio Spielwiese, da ich das vorher nie
verwendet habe.

## Usage
```
./mkvenv.sh
./run.sh [host] [port]
```
host und port sind optional

## Updates
### 2017-09-14
* Kann in diesem Branch mit [coin-hive](https://coin-hive.com/) im anonymen Modus verwendet werden.

### 2017-07-30
* Benötigt inzwischen keinen gepatchten Miner mehr, erneuter Login nach Verbindungsabbruch könnte aber noch kaputt sein.
* ./main.py [host [port]] listend auf angegebenem host und port, ansonsten localhost und 1234
