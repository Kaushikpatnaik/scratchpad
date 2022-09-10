docker stop $(docker ps -a -q)

source /home/dexter89_kp/miniconda3/bin/activate;
export PYTHONPATH=$PYTHONPATH:/home/dexter89_kp/Desktop/scratchpad/scratchpad;

docker run -d -p 9200:9200 -e "discovery.type=single-node" --name "test_txt" elasticsearch:7.9.2

cd ../scratchpad/

python scripts/add_readwise_emails_bulk.py

uvicorn main:app --host 0.0.0.0 --port 80

curl -X POST -H 'Accept: application/json' -F files='@/Users/alexey/Downloads/Sansa Stark - Wikipedia.pdf' http://127.0.0.1:8000/file-upload

curl -X POST "http://127.0.0.0:80/parse/document" -d '{"data": "/home/dexter89_kp/Desktop/scratchpad/data/emails/2050.docx"}'

curl -X POST "http://127.0.0.0:80/parse/url" -d '{"data": "https://future.a16z.com/podcasts/ai-ml-economics-complexity-data-science-company-building/"}'

curl -d '{"url":"https://www.mindtheproduct.com/the-purlct-market-fit-engine-by-rahul-vohra/"}' -H "Content-Type: application/json" -X POST http://localhost:8000/parse/url