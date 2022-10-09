docker kill $(docker ps -q)
cd frontend
docker build ./ -f ./DOCKERFILE-FRONTEND -t scratchpad-docker:frontend_0.2
cd ..
cd scratchpad
docker build ./ -f ./DOCKERFILE -t scratchpad-docker:0.9
cd ..
docker-compose -f docker-compose.yml up