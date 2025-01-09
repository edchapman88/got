date=$(date '+%Y-%m-%d_%H:%M:%S')

scp blue@$HILBERT_VM:/var/log/telegraf/telegraf.json ~/projects/got/experiments/$1/logs/hilbert/$date.json

scp blue@$KLEENE_VM:/var/log/telegraf/telegraf.json ~/projects/got/experiments/$1/logs/kleene/$date.json

scp blue@$KLEENE_VM:/home/blue/got_logs/* ~/projects/got/experiments/$1/logs/kleene
