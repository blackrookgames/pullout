shdir="$(dirname "$BASH_SOURCE")"

if [ "$#" -lt 1 ]; then
    echo "$BASH_SOURCE <python>"
    exit
fi

python=$1

$python ./main.py --crypto BTC,ETH,SOL,XRP,DOGE --ex_pfx USD --time12 --interval 15 --sellall --log_clear