shdir="$(dirname "$BASH_SOURCE")"

if [ "$#" -lt 1 ]; then
    echo "$BASH_SOURCE <python>"
    exit
fi

python=$1

$python ./main.py --ex_pfx USD --time12 --count 5 --interval 15 --sellall