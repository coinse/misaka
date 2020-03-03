git checkout -- misaka/
git apply $1
sh build.sh
python run_test.py
