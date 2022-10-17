cp frontend/config.yaml ./config.yaml
docker kill $(docker ps -q)
cp ./config.yaml frontend/config.yaml
cd frontend
docker build ./ -f ./DOCKERFILE-FRONTEND -t scratchpad-docker:frontend_0.2
cd ..
cd scratchpad
docker build ./ -f ./DOCKERFILE -t scratchpad-docker:0.9
cd ..
docker-compose -f docker-compose.yml up