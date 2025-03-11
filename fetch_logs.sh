date=$(date '+%Y-%m-%d_%H:%M:%S')

scp ed@$HILBERT:/var/log/telegraf/telegraf.json ~/projects/got/experiments/$1/logs/hilbert/$date.json

scp ed@$HILBERT:/home/ed/blue_logs/* ~/projects/got/experiments/$1/logs/hilbert

scp ed@$KLEENE:/var/log/telegraf/telegraf.json ~/projects/got/experiments/$1/logs/kleene/$date.json

scp ed@$KLEENE:/home/ed/got_logs/* ~/projects/got/experiments/$1/logs/kleene
