git checkout -- misaka/
git apply faults/$1.diff
sh build.sh
python run_test.py > faults/$1.txt
