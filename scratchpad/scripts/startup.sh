source /home/dexter89_kp/miniconda3/bin/activate;
export PYTHONPATH=$PYTHONPATH:/home/dexter89_kp/Desktop/scratchpad;
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.9.2

